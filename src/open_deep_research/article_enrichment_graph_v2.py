"""Article Enrichment Graph - Version avec Logging Intégré.

Cette version inclut un système de logging structuré dans le terminal.
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

# Import des loggers
from open_deep_research.utils_logging import (
    get_deep_researcher_logger,
    get_enrichment_logger,
    log_node_entry,
    log_node_exit,
    log_article_info,
    log_search_phase,
    log_amazon_results,
    log_web_results,
    log_routing_decision,
    log_tavily_call,
    log_error,
    log_final_summary,
)

# Initialize configurable model
configurable_model = init_chat_model(
    configurable_fields=("model", "max_tokens", "api_key"),
)

# Logger principal
logger = get_enrichment_logger()


# =============================================================================
# NODE 1: CREATE RESEARCH BRIEF
# =============================================================================

async def create_research_brief(
    state: EnrichmentState,
    config: RunnableConfig
) -> Command[Literal["deep_researcher"]]:
    """
    Transform article payload into a structured research brief.
    """
    log_node_entry(logger, "create_research_brief", state)

    article = state["article_payload"]

    # Log article info
    log_article_info(logger, state)

    # Format article into multi-language queries
    queries = format_article_for_search({
        "ean": article.ean,
        "marque": article.marque,
        "libelle": article.libelle,
        "reference_fournisseur": article.reference_fournisseur,
    })

    logger.info("📝 [BRIEF_CREATION] Génération du brief de recherche")
    logger.info(f"  • Requêtes générées: {sum(len(q) for q in queries.values())}")
    for lang, lang_queries in queries.items():
        if lang_queries:
            logger.info(f"    - {lang}: {len(lang_queries)} requêtes")

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

    log_node_exit(logger, "create_research_brief", "deep_researcher")

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
    """
    researcher_logger = get_deep_researcher_logger()
    log_node_entry(researcher_logger, "deep_researcher", state)

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
    amazon_queries = []
    if queries.get("universal"):
        amazon_queries.extend(queries["universal"])
    if queries.get("english"):
        amazon_queries.extend(queries["english"][:2])
    if queries.get("french"):
        amazon_queries.extend(queries["french"][:1])

    amazon_queries = amazon_queries[:enrichment_config.max_amazon_searches]

    log_search_phase(researcher_logger, 1, "Recherche Amazon Multi-pays", amazon_queries)

    try:
        amazon_results_raw = await tavily_search_amazon.ainvoke({
            "queries": amazon_queries,
            "max_results": enrichment_config.tavily_max_results
        })

        researcher_logger.info("✅ [PHASE 1] Recherche Amazon terminée")

        # Parse Amazon results
        amazon_products = parse_amazon_results(amazon_results_raw, article)
        log_amazon_results(researcher_logger, amazon_products)

        log_tavily_call(researcher_logger, "tavily_search_amazon", amazon_queries, len(amazon_products), success=True)

    except Exception as e:
        log_error(researcher_logger, "deep_researcher", f"Erreur Phase 1 (Amazon): {str(e)}")
        amazon_products = []

    # =========================================================================
    # DECISION POINT: If Amazon found, route to REFERENTIEL
    # =========================================================================
    if amazon_products:
        researcher_logger.info(f"🎯 [DECISION] {len(amazon_products)} produit(s) Amazon trouvé(s)")

        # Calculate confidence score
        confidence = calculate_amazon_confidence(amazon_products[0], article, enrichment_config)
        researcher_logger.info(f"📊 [CONFIDENCE] Score calculé: {confidence:.2f}")

        if should_route_to_referentiel(confidence, enrichment_config):
            researcher_logger.info(f"✅ [ROUTING] Confidence {confidence:.2f} >= {enrichment_config.scoring_thresholds.referentiel_min}")
            researcher_logger.info(f"➡️  [ROUTING] Direction: REFERENTIEL (Amazon)")

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

            log_routing_decision(researcher_logger, routing_decision)
            log_node_exit(researcher_logger, "deep_researcher", "amazon_subgraph")

            return Command(
                goto="amazon_subgraph",
                update={
                    "routing_decision": routing_decision,
                    "amazon_products_found": amazon_products,
                    "enrichment_type": "REFERENTIEL",
                    "search_iterations_count": len(amazon_queries),
                }
            )
        else:
            researcher_logger.info(f"⚠️  [ROUTING] Confidence {confidence:.2f} < {enrichment_config.scoring_thresholds.referentiel_min}")
            researcher_logger.info("➡️  [ROUTING] Passage à Phase 2 (Web)")

    else:
        researcher_logger.info("❌ [PHASE 1] Aucun produit Amazon trouvé")
        researcher_logger.info("➡️  [ROUTING] Passage à Phase 2 (Web)")

    # =========================================================================
    # PHASE 2: GENERAL WEB SEARCH
    # =========================================================================
    web_queries = []
    if queries.get("english"):
        web_queries.extend(queries["english"][:2])
    if queries.get("french"):
        web_queries.extend(queries["french"][:1])
    if queries.get("italian"):
        web_queries.extend(queries["italian"][:1])

    web_queries = web_queries[:enrichment_config.max_web_searches]

    log_search_phase(researcher_logger, 2, "Recherche Web Générale", web_queries)

    try:
        web_results_raw = await tavily_search_web.ainvoke({
            "queries": web_queries,
            "max_results": enrichment_config.tavily_max_results
        })

        researcher_logger.info("✅ [PHASE 2] Recherche web terminée")

        # Parse web results
        web_sources = parse_web_results(web_results_raw, article, enrichment_config)
        log_web_results(researcher_logger, web_sources)

        log_tavily_call(researcher_logger, "tavily_search_web", web_queries, len(web_sources), success=True)

    except Exception as e:
        log_error(researcher_logger, "deep_researcher", f"Erreur Phase 2 (Web): {str(e)}")
        web_sources = []

    # =========================================================================
    # DECISION POINT: If web sources found, route to WEB
    # =========================================================================
    if len(web_sources) >= enrichment_config.scoring_thresholds.min_web_sources:
        researcher_logger.info(f"🎯 [DECISION] {len(web_sources)} source(s) web trouvée(s)")

        # Calculate confidence based on consensus
        confidence = calculate_web_confidence(web_sources, enrichment_config)
        researcher_logger.info(f"📊 [CONFIDENCE] Score calculé: {confidence:.2f}")

        if should_route_to_web(confidence, len(web_sources), enrichment_config):
            researcher_logger.info(f"✅ [ROUTING] Confidence {confidence:.2f} >= {enrichment_config.scoring_thresholds.web_min}")
            researcher_logger.info(f"➡️  [ROUTING] Direction: WEB (Multi-sources)")

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

            log_routing_decision(researcher_logger, routing_decision)
            log_node_exit(researcher_logger, "deep_researcher", "web_subgraph")

            return Command(
                goto="web_subgraph",
                update={
                    "routing_decision": routing_decision,
                    "web_sources_found": web_sources,
                    "enrichment_type": "WEB",
                    "search_iterations_count": len(amazon_queries) + len(web_queries),
                }
            )
        else:
            researcher_logger.info(f"⚠️  [ROUTING] Confidence {confidence:.2f} < {enrichment_config.scoring_thresholds.web_min}")
            researcher_logger.info("➡️  [ROUTING] Passage à Phase 3 (GENERATIF)")

    else:
        researcher_logger.info(f"❌ [PHASE 2] Seulement {len(web_sources)} source(s) (min: {enrichment_config.scoring_thresholds.min_web_sources})")
        researcher_logger.info("➡️  [ROUTING] Passage à Phase 3 (GENERATIF)")

    # =========================================================================
    # DECISION POINT: Check GENERATIF eligibility
    # =========================================================================
    researcher_logger.info("🔍 [PHASE 3] Vérification éligibilité GENERATIF")

    has_images = article.images_disponibles and article.images_urls
    has_technical_data = (
        article.specifications_techniques or
        article.fiche_technique_url or
        article.documents_techniques
    )

    researcher_logger.info(f"  • Images: {'✅' if has_images else '❌'}")
    researcher_logger.info(f"  • Données techniques: {'✅' if has_technical_data else '❌'}")

    if has_images and has_technical_data:
        researcher_logger.info("✅ [ROUTING] Éligible pour GENERATIF")
        researcher_logger.info("➡️  [ROUTING] Direction: GENERATIF (IA Native)")

        routing_decision = RoutingDecision(
            enrichment_type="GENERATIF",
            confidence_score=0.65,
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

        log_routing_decision(researcher_logger, routing_decision)
        log_node_exit(researcher_logger, "deep_researcher", "generative_subgraph")

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
    researcher_logger.info("❌ [ROUTING] Données insuffisantes pour tous les types")
    researcher_logger.info("➡️  [ROUTING] Direction: EN_ATTENTE (Pending)")

    missing_data = []
    if not has_images:
        missing_data.append("Images produit")
    if not has_technical_data:
        missing_data.append("Données techniques ou fiche technique")

    researcher_logger.info(f"⏳ [MISSING_DATA] Données manquantes:")
    for item in missing_data:
        researcher_logger.info(f"    • {item}")

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

    log_routing_decision(researcher_logger, routing_decision)
    log_node_exit(researcher_logger, "deep_researcher", "pending_node")

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
    """Parse Tavily Amazon search results."""
    products = []
    import re

    url_pattern = r'URL: (https?://[^\s]+)'
    urls = re.findall(url_pattern, results_raw)

    for url in urls:
        asin = extract_asin_from_url(url)
        domain = extract_domain_from_url(url)

        if asin and domain:
            title_pattern = rf'(\d+)\. (.+?)\n\s+URL: {re.escape(url)}'
            title_match = re.search(title_pattern, results_raw)
            title = title_match.group(2) if title_match else None

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
    """Parse Tavily web search results."""
    sources = []
    import re

    url_pattern = r'URL: (https?://[^\s]+)'
    urls = re.findall(url_pattern, results_raw)

    for url in urls:
        domain = extract_domain_from_url(url)

        title_pattern = rf'(\d+)\. (.+?)\n\s+URL: {re.escape(url)}'
        title_match = re.search(title_pattern, results_raw)
        title = title_match.group(2) if title_match else None

        score_pattern = rf'URL: {re.escape(url)}.*?Score: ([\d.]+)'
        score_match = re.search(score_pattern, results_raw, re.DOTALL)
        score = float(score_match.group(1)) if score_match else 0.0

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
    """Calculate confidence score for Amazon product match."""
    ean_match = False
    brand_match = False
    model_match = False
    category_match = False

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
    """Calculate confidence score based on web sources consensus."""
    if not sources:
        return 0.0

    avg_score = sum(s.relevance_score for s in sources) / len(sources)
    source_count_boost = min(len(sources) * 0.05, 0.15)
    return min(avg_score + source_count_boost, 1.0)


# =============================================================================
# STUB NODES FOR SUBGRAPHS
# =============================================================================

async def amazon_subgraph(
    state: EnrichmentState,
    config: RunnableConfig
) -> Command[Literal["output_results"]]:
    """STUB: Amazon enrichment subgraph."""
    log_node_entry(logger, "amazon_subgraph (STUB)", state)
    logger.info("📦 [STUB] Amazon Subgraph - À implémenter")
    log_node_exit(logger, "amazon_subgraph", "output_results")

    return Command(
        goto="output_results",
        update={"enrichment_status": "STUB_REFERENTIEL"}
    )


async def web_subgraph(
    state: EnrichmentState,
    config: RunnableConfig
) -> Command[Literal["output_results"]]:
    """STUB: Web enrichment subgraph."""
    log_node_entry(logger, "web_subgraph (STUB)", state)
    logger.info("🌐 [STUB] Web Subgraph - À implémenter")
    log_node_exit(logger, "web_subgraph", "output_results")

    return Command(
        goto="output_results",
        update={"enrichment_status": "STUB_WEB"}
    )


async def generative_subgraph(
    state: EnrichmentState,
    config: RunnableConfig
) -> Command[Literal["output_results"]]:
    """STUB: Generative enrichment subgraph."""
    log_node_entry(logger, "generative_subgraph (STUB)", state)
    logger.info("✨ [STUB] Generative Subgraph - À implémenter")
    log_node_exit(logger, "generative_subgraph", "output_results")

    return Command(
        goto="output_results",
        update={"enrichment_status": "STUB_GENERATIF"}
    )


async def pending_node(
    state: EnrichmentState,
    config: RunnableConfig
) -> Command[Literal["output_results"]]:
    """Handle articles with missing data."""
    log_node_entry(logger, "pending_node", state)
    logger.info("⏳ [PENDING] Article en attente - Données manquantes")
    log_node_exit(logger, "pending_node", "output_results")

    return Command(
        goto="output_results",
        update={"enrichment_status": "EN_ATTENTE"}
    )


# =============================================================================
# NODE: OUTPUT RESULTS
# =============================================================================

async def output_results(
    state: EnrichmentState,
    config: RunnableConfig
) -> Command[Literal["__end__"]]:
    """Output the search results and routing decision."""
    log_node_entry(logger, "output_results", state)

    # Log final summary
    log_final_summary(logger, state)

    # Store final state
    log_node_exit(logger, "output_results", "END")

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
    """Create and compile the article enrichment graph."""
    logger.info("🏗️  [GRAPH] Création du graph d'enrichissement...")

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

    # Compile graph
    graph = graph_builder.compile()

    logger.info("✅ [GRAPH] Graph compilé avec succès")

    return graph


# Export the graph
enrichment_graph = create_enrichment_graph()
