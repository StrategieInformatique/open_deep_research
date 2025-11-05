"""Article Enrichment Graph - Main implementation.

This module implements the cascade enrichment workflow:
- REFERENTIEL (Amazon)
- WEB (Multi-sources)
- GENERATIF (IA Native)
- EN_ATTENTE (Pending)
"""

import asyncio
import json
from typing import Literal, Dict, Any, List
from datetime import datetime

from langchain.chat_models import init_chat_model
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from open_deep_research.configuration_enrichment import (
    EnrichmentConfiguration,
    calculate_matching_score,
    should_route_to_referentiel,
    should_route_to_web,
)
from open_deep_research.prompts_enrichment import (
    article_to_research_brief_prompt,
    deep_researcher_article_enrichment_prompt,
)
from open_deep_research.state_enrichment import (
    EnrichmentState,
    ArticlePayload,
    ResearchBrief,
    AmazonProduct,
    WebSource,
    RoutingDecision,
    extract_asin_from_url,
    extract_domain_from_url,
)
from open_deep_research.utils_enrichment import (
    tavily_search_amazon,
    tavily_search_web,
    tavily_extract_content,
    think_tool,
    format_article_for_search,
    get_today_str,
)

# Initialize configurable model
configurable_model = init_chat_model(
    configurable_fields=("model", "max_tokens", "api_key"),
)


# =============================================================================
# NODE 1: CREATE RESEARCH BRIEF
# =============================================================================

async def create_research_brief(
    state: EnrichmentState,
    config: RunnableConfig
) -> Command[Literal["deep_researcher"]]:
    """
    Transform article payload into a structured research brief.

    This is a simple transformation step that prepares the article data
    for the deep_researcher node.

    Args:
        state: Current enrichment state with article payload
        config: Runtime configuration

    Returns:
        Command to proceed to deep_researcher with research brief
    """
    article = state["article_payload"]

    # Format article into multi-language queries
    queries = format_article_for_search({
        "ean": article.ean,
        "marque": article.marque,
        "libelle": article.libelle,
        "reference_fournisseur": article.reference_fournisseur,
    })

    # Create research brief
    research_brief = ResearchBrief(
        product_identity={
            "ean": article.ean,
            "brand": article.marque,
            "model": article.libelle,
            "supplier_reference": article.reference_fournisseur,
            "category": article.famille_produit,
        },
        search_queries=queries,
        search_strategy={
            "phase_1": "Amazon multi-country search",
            "phase_2": "General web search (if Amazon fails)",
            "phase_3": "Technical documentation search",
        },
        success_criteria={
            "referentiel": "ASIN found with confidence > 0.75",
            "web": "2+ relevant sources with score > 0.5",
            "generatif": "Images + technical data available",
        }
    )

    return Command(
        goto="deep_researcher",
        update={
            "research_brief": research_brief,
            "search_languages_used": ["french", "english", "italian", "spanish", "german"],
        }
    )


# =============================================================================
# NODE 2: DEEP RESEARCHER (Main Research & Routing)
# =============================================================================

async def deep_researcher(
    state: EnrichmentState,
    config: RunnableConfig
) -> Command[Literal["amazon_subgraph", "web_subgraph", "generative_subgraph", "pending_node"]]:
    """
    Conduct comprehensive research and decide routing.

    This node performs:
    1. Phase 1: Amazon multi-country search
    2. Phase 2: General web search (if Amazon fails)
    3. Phase 3: Technical documentation search
    4. Routing decision based on findings

    Args:
        state: Current enrichment state with article payload and research brief
        config: Runtime configuration

    Returns:
        Command to route to appropriate subgraph
    """
    # =========================================================================
    # SETUP
    # =========================================================================
    enrichment_config = EnrichmentConfiguration()
    article = state["article_payload"]
    research_brief = state.get("research_brief")

    # Extract search queries
    queries = research_brief.search_queries if research_brief else {}

    # =========================================================================
    # PHASE 1: AMAZON MULTI-COUNTRY SEARCH
    # =========================================================================
    print("\n🔍 PHASE 1: Searching Amazon across multiple countries...")

    amazon_queries = []
    if queries.get("universal"):
        amazon_queries.extend(queries["universal"])
    if queries.get("english"):
        amazon_queries.extend(queries["english"][:2])  # Limit to 2
    if queries.get("french"):
        amazon_queries.extend(queries["french"][:1])  # Limit to 1

    # Limit total Amazon queries to max_amazon_searches
    amazon_queries = amazon_queries[:enrichment_config.max_amazon_searches]

    amazon_results_raw = await tavily_search_amazon.ainvoke({
        "queries": amazon_queries,
        "max_results": enrichment_config.tavily_max_results
    })

    print(f"✅ Amazon search completed. Results:\n{amazon_results_raw[:500]}...")

    # Parse Amazon results
    amazon_products = parse_amazon_results(amazon_results_raw, article)

    # =========================================================================
    # DECISION POINT: If Amazon found, route to REFERENTIEL
    # =========================================================================
    if amazon_products:
        print(f"\n✅ Found {len(amazon_products)} Amazon product(s)!")

        # Calculate confidence score
        confidence = calculate_amazon_confidence(amazon_products[0], article, enrichment_config)

        if should_route_to_referentiel(confidence, enrichment_config):
            print(f"✅ Confidence score {confidence:.2f} >= threshold. Routing to REFERENTIEL.")

            routing_decision = RoutingDecision(
                enrichment_type="REFERENTIEL",
                confidence_score=confidence,
                justification=f"Product found on Amazon with {len(amazon_products)} match(es). Confidence: {confidence:.2f}",
                amazon_data=amazon_products,
                web_sources=None,
                generatif_data=None,
                missing_data=None,
                search_summary={
                    "phase": "Amazon",
                    "queries_count": len(amazon_queries),
                    "results_count": len(amazon_products),
                    "languages": ["universal", "english", "french"],
                }
            )

            return Command(
                goto="amazon_subgraph",
                update={
                    "routing_decision": routing_decision,
                    "amazon_products_found": amazon_products,
                    "enrichment_type": "REFERENTIEL",
                    "search_iterations_count": len(amazon_queries),
                }
            )

    print("\n❌ No suitable Amazon products found. Proceeding to Phase 2...")

    # =========================================================================
    # PHASE 2: GENERAL WEB SEARCH
    # =========================================================================
    print("\n🔍 PHASE 2: Searching general web...")

    web_queries = []
    if queries.get("english"):
        web_queries.extend(queries["english"][:2])
    if queries.get("french"):
        web_queries.extend(queries["french"][:1])
    if queries.get("italian"):
        web_queries.extend(queries["italian"][:1])

    # Limit total web queries
    web_queries = web_queries[:enrichment_config.max_web_searches]

    web_results_raw = await tavily_search_web.ainvoke({
        "queries": web_queries,
        "max_results": enrichment_config.tavily_max_results
    })

    print(f"✅ Web search completed. Results:\n{web_results_raw[:500]}...")

    # Parse web results
    web_sources = parse_web_results(web_results_raw, article, enrichment_config)

    # =========================================================================
    # DECISION POINT: If web sources found, route to WEB
    # =========================================================================
    if len(web_sources) >= enrichment_config.scoring_thresholds.min_web_sources:
        print(f"\n✅ Found {len(web_sources)} relevant web source(s)!")

        # Calculate confidence based on consensus
        confidence = calculate_web_confidence(web_sources, enrichment_config)

        if should_route_to_web(confidence, len(web_sources), enrichment_config):
            print(f"✅ Confidence score {confidence:.2f} >= threshold. Routing to WEB.")

            routing_decision = RoutingDecision(
                enrichment_type="WEB",
                confidence_score=confidence,
                justification=f"Product found on {len(web_sources)} web source(s). Confidence: {confidence:.2f}",
                amazon_data=None,
                web_sources=web_sources,
                generatif_data=None,
                missing_data=None,
                search_summary={
                    "phase": "Web",
                    "queries_count": len(web_queries),
                    "results_count": len(web_sources),
                    "languages": ["english", "french", "italian"],
                }
            )

            return Command(
                goto="web_subgraph",
                update={
                    "routing_decision": routing_decision,
                    "web_sources_found": web_sources,
                    "enrichment_type": "WEB",
                    "search_iterations_count": len(amazon_queries) + len(web_queries),
                }
            )

    print("\n❌ Insufficient web sources found. Checking for GENERATIF eligibility...")

    # =========================================================================
    # DECISION POINT: Check GENERATIF eligibility
    # =========================================================================
    has_images = article.images_disponibles and article.images_urls
    has_technical_data = (
        article.specifications_techniques or
        article.fiche_technique_url or
        article.documents_techniques
    )

    if has_images and has_technical_data:
        print("\n✅ Article has required data for GENERATIF enrichment!")

        routing_decision = RoutingDecision(
            enrichment_type="GENERATIF",
            confidence_score=0.65,  # Default for generative
            justification="Product not found online but has images and technical data for AI generation.",
            amazon_data=None,
            web_sources=None,
            generatif_data={
                "images": article.images_urls,
                "technical_specs": article.specifications_techniques,
                "technical_docs": article.documents_techniques or [],
                "datasheet_url": article.fiche_technique_url,
            },
            missing_data=None,
            search_summary={
                "phase": "Generative",
                "queries_count": len(amazon_queries) + len(web_queries),
                "results_count": 0,
                "reason": "Not found online, using available data",
            }
        )

        return Command(
            goto="generative_subgraph",
            update={
                "routing_decision": routing_decision,
                "enrichment_type": "GENERATIF",
                "search_iterations_count": len(amazon_queries) + len(web_queries),
            }
        )

    # =========================================================================
    # FALLBACK: Route to EN_ATTENTE
    # =========================================================================
    print("\n❌ Insufficient data for enrichment. Routing to EN_ATTENTE...")

    missing_data = []
    if not has_images:
        missing_data.append("Images produit")
    if not has_technical_data:
        missing_data.append("Données techniques ou fiche technique")

    routing_decision = RoutingDecision(
        enrichment_type="EN_ATTENTE",
        confidence_score=0.0,
        justification="Product not found online and missing required data for generative enrichment.",
        amazon_data=None,
        web_sources=None,
        generatif_data=None,
        missing_data=missing_data,
        search_summary={
            "phase": "Pending",
            "queries_count": len(amazon_queries) + len(web_queries),
            "results_count": 0,
            "reason": "Missing required data",
        }
    )

    return Command(
        goto="pending_node",
        update={
            "routing_decision": routing_decision,
            "enrichment_type": "EN_ATTENTE",
            "missing_data_list": missing_data,
            "search_iterations_count": len(amazon_queries) + len(web_queries),
        }
    )


# =============================================================================
# HELPER FUNCTIONS FOR PARSING RESULTS
# =============================================================================

def parse_amazon_results(
    results_raw: str,
    article: ArticlePayload
) -> List[AmazonProduct]:
    """
    Parse Tavily Amazon search results into structured AmazonProduct objects.

    Args:
        results_raw: Raw string results from tavily_search_amazon
        article: Original article payload

    Returns:
        List of AmazonProduct objects
    """
    products = []

    # Simple parsing - in production, this would use structured Tavily responses
    # For now, we'll do regex-based parsing from the formatted string
    import re

    # Find all URLs in the results
    url_pattern = r'URL: (https?://[^\s]+)'
    urls = re.findall(url_pattern, results_raw)

    for url in urls:
        asin = extract_asin_from_url(url)
        domain = extract_domain_from_url(url)

        if asin and domain:
            # Extract title (line before URL)
            title_pattern = rf'(\d+)\. (.+?)\n\s+URL: {re.escape(url)}'
            title_match = re.search(title_pattern, results_raw)
            title = title_match.group(2) if title_match else None

            # Extract score
            score_pattern = rf'URL: {re.escape(url)}.*?Score: ([\d.]+)'
            score_match = re.search(score_pattern, results_raw, re.DOTALL)
            score = float(score_match.group(1)) if score_match else 0.0

            products.append(AmazonProduct(
                asin=asin,
                domain=domain,
                url=url,
                title=title,
                metadata={"tavily_score": score}
            ))

    return products


def parse_web_results(
    results_raw: str,
    article: ArticlePayload,
    config: EnrichmentConfiguration
) -> List[WebSource]:
    """
    Parse Tavily web search results into structured WebSource objects.

    Args:
        results_raw: Raw string results from tavily_search_web
        article: Original article payload
        config: Enrichment configuration

    Returns:
        List of WebSource objects with score >= threshold
    """
    sources = []

    import re

    # Find all URLs and scores
    url_pattern = r'URL: (https?://[^\s]+)'
    urls = re.findall(url_pattern, results_raw)

    for url in urls:
        domain = extract_domain_from_url(url)

        # Extract title
        title_pattern = rf'(\d+)\. (.+?)\n\s+URL: {re.escape(url)}'
        title_match = re.search(title_pattern, results_raw)
        title = title_match.group(2) if title_match else None

        # Extract score
        score_pattern = rf'URL: {re.escape(url)}.*?Score: ([\d.]+)'
        score_match = re.search(score_pattern, results_raw, re.DOTALL)
        score = float(score_match.group(1)) if score_match else 0.0

        # Only include sources above threshold
        if score >= config.scoring_thresholds.tavily_relevance_threshold:
            sources.append(WebSource(
                url=url,
                title=title,
                domain=domain,
                relevance_score=score,
                metadata={"tavily_score": score}
            ))

    return sources


def calculate_amazon_confidence(
    product: AmazonProduct,
    article: ArticlePayload,
    config: EnrichmentConfiguration
) -> float:
    """
    Calculate confidence score for Amazon product match.

    Args:
        product: Amazon product found
        article: Original article payload
        config: Enrichment configuration

    Returns:
        Confidence score (0.0 to 1.0)
    """
    # For now, simple heuristic based on having an ASIN
    # In production, this would check EAN, brand, model matching

    ean_match = False  # Would need to fetch Amazon product data to verify
    brand_match = False  # Would check if brand appears in title
    model_match = False  # Would check if model appears in title
    category_match = False

    # Simple title-based matching if title available
    if product.title and article.marque:
        brand_match = article.marque.lower() in product.title.lower()

    if product.title and article.libelle:
        model_match = article.libelle.lower() in product.title.lower()

    return calculate_matching_score(
        ean_match=ean_match,
        brand_match=brand_match,
        model_match=model_match,
        category_match=category_match,
        config=config
    )


def calculate_web_confidence(
    sources: List[WebSource],
    config: EnrichmentConfiguration
) -> float:
    """
    Calculate confidence score based on web sources consensus.

    Args:
        sources: List of web sources found
        config: Enrichment configuration

    Returns:
        Confidence score (0.0 to 1.0)
    """
    if not sources:
        return 0.0

    # Average of relevance scores
    avg_score = sum(s.relevance_score for s in sources) / len(sources)

    # Boost if multiple sources
    source_count_boost = min(len(sources) * 0.05, 0.15)

    return min(avg_score + source_count_boost, 1.0)


# =============================================================================
# STUB NODES FOR SUBGRAPHS (Not implemented yet)
# =============================================================================

async def amazon_subgraph(
    state: EnrichmentState,
    config: RunnableConfig
) -> Command[Literal["output_results"]]:
    """
    STUB: Amazon enrichment subgraph (REFERENTIEL).

    To be implemented later. For now, just passes through.
    """
    print("\n📦 Amazon Subgraph (STUB - Not implemented yet)")

    return Command(
        goto="output_results",
        update={
            "enrichment_status": "STUB_REFERENTIEL"
        }
    )


async def web_subgraph(
    state: EnrichmentState,
    config: RunnableConfig
) -> Command[Literal["output_results"]]:
    """
    STUB: Web enrichment subgraph (WEB).

    To be implemented later. For now, just passes through.
    """
    print("\n🌐 Web Subgraph (STUB - Not implemented yet)")

    return Command(
        goto="output_results",
        update={
            "enrichment_status": "STUB_WEB"
        }
    )


async def generative_subgraph(
    state: EnrichmentState,
    config: RunnableConfig
) -> Command[Literal["output_results"]]:
    """
    STUB: Generative enrichment subgraph (GENERATIF).

    To be implemented later. For now, just passes through.
    """
    print("\n✨ Generative Subgraph (STUB - Not implemented yet)")

    return Command(
        goto="output_results",
        update={
            "enrichment_status": "STUB_GENERATIF"
        }
    )


async def pending_node(
    state: EnrichmentState,
    config: RunnableConfig
) -> Command[Literal["output_results"]]:
    """
    Handle articles with missing data (EN_ATTENTE).
    """
    print("\n⏳ Pending Node - Missing data identified")

    return Command(
        goto="output_results",
        update={
            "enrichment_status": "EN_ATTENTE"
        }
    )


# =============================================================================
# NODE: OUTPUT RESULTS (Replaces report_generator for testing)
# =============================================================================

async def output_results(
    state: EnrichmentState,
    config: RunnableConfig
) -> Command[Literal["__end__"]]:
    """
    Output the search results and routing decision for testing.

    This replaces the full report generator to allow testing and adjustment
    of the deep_researcher before implementing subgraphs.

    Args:
        state: Current enrichment state with all search results
        config: Runtime configuration

    Returns:
        Command to end the workflow
    """
    print("\n" + "="*80)
    print("📊 ENRICHMENT RESULTS")
    print("="*80)

    routing = state.get("routing_decision")
    article = state["article_payload"]

    # Article info
    print(f"\n📦 Article: {article.marque} {article.libelle}")
    if article.ean:
        print(f"   EAN: {article.ean}")
    if article.reference_fournisseur:
        print(f"   Ref: {article.reference_fournisseur}")

    # Routing decision
    if routing:
        print(f"\n🎯 ROUTING DECISION: {routing.enrichment_type}")
        print(f"   Confidence Score: {routing.confidence_score:.2f}")
        print(f"   Justification: {routing.justification}")

        # Search summary
        summary = routing.search_summary
        print(f"\n🔍 Search Summary:")
        print(f"   Phase: {summary.get('phase')}")
        print(f"   Queries: {summary.get('queries_count')}")
        print(f"   Results: {summary.get('results_count')}")
        if summary.get('languages'):
            print(f"   Languages: {', '.join(summary.get('languages', []))}")

        # Type-specific results
        if routing.enrichment_type == "REFERENTIEL" and routing.amazon_data:
            print(f"\n🛒 Amazon Products Found: {len(routing.amazon_data)}")
            for idx, product in enumerate(routing.amazon_data, 1):
                print(f"   {idx}. ASIN: {product.asin}")
                print(f"      Domain: {product.domain}")
                print(f"      URL: {product.url}")
                if product.title:
                    print(f"      Title: {product.title}")

        elif routing.enrichment_type == "WEB" and routing.web_sources:
            print(f"\n🌐 Web Sources Found: {len(routing.web_sources)}")
            for idx, source in enumerate(routing.web_sources, 1):
                print(f"   {idx}. Domain: {source.domain}")
                print(f"      Score: {source.relevance_score:.2f}")
                print(f"      URL: {source.url}")
                if source.title:
                    print(f"      Title: {source.title}")

        elif routing.enrichment_type == "GENERATIF" and routing.generatif_data:
            print(f"\n✨ Generative Data Available:")
            data = routing.generatif_data
            if data.get('images'):
                print(f"   Images: {len(data['images'])}")
            if data.get('technical_specs'):
                print(f"   Technical Specs: Yes")
            if data.get('datasheet_url'):
                print(f"   Datasheet: {data['datasheet_url']}")

        elif routing.enrichment_type == "EN_ATTENTE" and routing.missing_data:
            print(f"\n⏳ Missing Data:")
            for item in routing.missing_data:
                print(f"   - {item}")

    # Next node indication
    print(f"\n➡️  Next Node: {routing.enrichment_type}_subgraph")

    # Processing metadata
    if state.get("processing_start_time"):
        duration = (datetime.now() - state["processing_start_time"]).total_seconds()
        print(f"\n⏱️  Processing Time: {duration:.2f} seconds")

    print("\n" + "="*80)

    # Store final state
    return Command(
        goto=END,
        update={
            "processing_end_time": datetime.now(),
            "enrichment_status": "RESEARCH_COMPLETE"
        }
    )


# =============================================================================
# GRAPH ASSEMBLY
# =============================================================================

def create_enrichment_graph():
    """
    Create and compile the article enrichment graph.

    Returns:
        Compiled LangGraph workflow
    """
    # Create graph builder
    graph_builder = StateGraph(EnrichmentState)

    # Add nodes
    graph_builder.add_node("create_research_brief", create_research_brief)
    graph_builder.add_node("deep_researcher", deep_researcher)
    graph_builder.add_node("amazon_subgraph", amazon_subgraph)
    graph_builder.add_node("web_subgraph", web_subgraph)
    graph_builder.add_node("generative_subgraph", generative_subgraph)
    graph_builder.add_node("pending_node", pending_node)
    graph_builder.add_node("output_results", output_results)

    # Define edges
    graph_builder.add_edge(START, "create_research_brief")

    # create_research_brief → deep_researcher (set by Command)
    # deep_researcher → [subgraphs] (set by Command based on routing)
    # All subgraphs → output_results (set by Command)
    # output_results → END (set by Command)

    # Compile graph
    graph = graph_builder.compile()

    return graph


# =============================================================================
# ENTRY POINT FOR TESTING
# =============================================================================

# Export the graph for use by LangGraph
enrichment_graph = create_enrichment_graph()
