"""Utility functions and tools for Article Enrichment.

This module contains helper functions and Tavily tools for the enrichment workflow.
"""

import os
import re
from typing import List, Optional, Dict, Any
from langchain_core.tools import tool


# =============================================================================
# TAVILY TOOLS FOR ENRICHMENT
# =============================================================================

@tool
async def tavily_search_amazon(
    queries: List[str],
    max_results: int = 10
) -> str:
    """
    Search for products on Amazon across multiple countries using Tavily Search.

    This tool is optimized for finding products on Amazon sites:
    - amazon.fr, amazon.it, amazon.com, amazon.es, amazon.de, amazon.co.uk

    Args:
        queries: List of search queries (can be in multiple languages)
        max_results: Maximum results to return (default: 10)

    Returns:
        Formatted search results with URLs, titles, and snippets
    """
    try:
        from tavily import TavilyClient
    except ImportError:
        return "Error: Tavily client not installed. Install with: pip install tavily-python"

    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY environment variable not set"

    client = TavilyClient(api_key=api_key)

    # Amazon domains to search
    amazon_domains = [
        "amazon.fr",
        "amazon.it",
        "amazon.com",
        "amazon.es",
        "amazon.de",
        "amazon.co.uk"
    ]

    results = []
    for query in queries:
        try:
            # Search with domain restriction to Amazon sites
            response = client.search(
                query=query,
                search_depth="advanced",  # Better accuracy (2 credits)
                max_results=max_results,
                include_domains=amazon_domains
            )

            for result in response.get("results", []):
                url = result.get("url", "")
                title = result.get("title", "")
                content = result.get("content", "")
                score = result.get("score", 0.0)

                # Extract ASIN if this is an Amazon URL
                asin = extract_asin_from_url(url)
                domain = extract_domain_from_url(url)

                results.append({
                    "query": query,
                    "url": url,
                    "title": title,
                    "content": content,
                    "score": score,
                    "asin": asin,
                    "domain": domain
                })

        except Exception as e:
            results.append({
                "query": query,
                "error": str(e)
            })

    # Format results
    formatted = f"Found {len(results)} results across Amazon sites:\n\n"
    for idx, res in enumerate(results, 1):
        if "error" in res:
            formatted += f"{idx}. Query: {res['query']} - ERROR: {res['error']}\n\n"
        else:
            formatted += f"{idx}. {res['title']}\n"
            formatted += f"   URL: {res['url']}\n"
            if res.get('asin'):
                formatted += f"   ASIN: {res['asin']}\n"
            if res.get('domain'):
                formatted += f"   Domain: {res['domain']}\n"
            formatted += f"   Score: {res['score']:.2f}\n"
            formatted += f"   Content: {res['content'][:200]}...\n\n"

    return formatted


@tool
async def tavily_search_web(
    queries: List[str],
    max_results: int = 10
) -> str:
    """
    Search the web for products using Tavily Search (no domain restrictions).

    This tool is for general web search when products are not found on Amazon.
    It searches manufacturer sites, retailer sites, specification databases, etc.

    Args:
        queries: List of search queries (can be in multiple languages)
        max_results: Maximum results to return (default: 10)

    Returns:
        Formatted search results with URLs, titles, snippets, and relevance scores
    """
    try:
        from tavily import TavilyClient
    except ImportError:
        return "Error: Tavily client not installed. Install with: pip install tavily-python"

    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY environment variable not set"

    client = TavilyClient(api_key=api_key)

    results = []
    for query in queries:
        try:
            # General web search without domain restrictions
            response = client.search(
                query=query,
                search_depth="advanced",  # Better accuracy (2 credits)
                max_results=max_results
            )

            for result in response.get("results", []):
                url = result.get("url", "")
                title = result.get("title", "")
                content = result.get("content", "")
                score = result.get("score", 0.0)
                domain = extract_domain_from_url(url)

                results.append({
                    "query": query,
                    "url": url,
                    "title": title,
                    "content": content,
                    "score": score,
                    "domain": domain
                })

        except Exception as e:
            results.append({
                "query": query,
                "error": str(e)
            })

    # Format results
    formatted = f"Found {len(results)} web results:\n\n"
    for idx, res in enumerate(results, 1):
        if "error" in res:
            formatted += f"{idx}. Query: {res['query']} - ERROR: {res['error']}\n\n"
        else:
            formatted += f"{idx}. {res['title']}\n"
            formatted += f"   URL: {res['url']}\n"
            formatted += f"   Domain: {res['domain']}\n"
            formatted += f"   Score: {res['score']:.2f}\n"
            formatted += f"   Content: {res['content'][:200]}...\n\n"

    return formatted


@tool
async def tavily_extract_content(
    urls: List[str],
    extract_depth: str = "advanced"
) -> str:
    """
    Extract content from web pages or PDFs using Tavily Extract.

    Useful for extracting technical datasheets, product specifications, etc.

    Args:
        urls: List of URLs to extract content from
        extract_depth: "basic" or "advanced" (default: "advanced")

    Returns:
        Extracted content from the URLs
    """
    try:
        from tavily import TavilyClient
    except ImportError:
        return "Error: Tavily client not installed. Install with: pip install tavily-python"

    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY environment variable not set"

    client = TavilyClient(api_key=api_key)

    results = []
    for url in urls:
        try:
            response = client.extract(
                urls=[url],
                extract_depth=extract_depth
            )

            for result in response.get("results", []):
                raw_content = result.get("raw_content", "")
                results.append({
                    "url": url,
                    "content": raw_content[:2000] if raw_content else "No content extracted"
                })

        except Exception as e:
            results.append({
                "url": url,
                "error": str(e)
            })

    # Format results
    formatted = f"Extracted content from {len(results)} URLs:\n\n"
    for idx, res in enumerate(results, 1):
        if "error" in res:
            formatted += f"{idx}. URL: {res['url']} - ERROR: {res['error']}\n\n"
        else:
            formatted += f"{idx}. URL: {res['url']}\n"
            formatted += f"   Content preview: {res['content'][:500]}...\n\n"

    return formatted


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def extract_asin_from_url(url: str) -> Optional[str]:
    """
    Extract ASIN from an Amazon URL.

    Examples:
        https://www.amazon.fr/dp/B08X123456 → B08X123456
        https://www.amazon.com/Product/dp/B123456789/ref=... → B123456789

    Args:
        url: Amazon product URL

    Returns:
        ASIN string (10 characters) or None if not found
    """
    if not url:
        return None

    # Pattern to match ASIN in Amazon URLs
    # ASIN is always 10 characters, usually after /dp/ or /product/
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/product/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def extract_domain_from_url(url: str) -> Optional[str]:
    """
    Extract domain from URL.

    Example:
        https://www.amazon.fr/dp/B08X123456 → amazon.fr

    Args:
        url: Full URL

    Returns:
        Domain string or None
    """
    if not url:
        return None

    match = re.search(r'https?://(?:www\.)?([^/]+)', url)
    if match:
        return match.group(1)

    return None


def format_article_for_search(article: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Format article payload into multi-language search queries.

    Args:
        article: Article payload dictionary

    Returns:
        Dictionary with language-specific queries
    """
    ean = article.get("ean", "")
    brand = article.get("marque", "")
    model = article.get("libelle", "")
    reference = article.get("reference_fournisseur", "")

    queries = {
        "universal": [],
        "french": [],
        "english": [],
        "italian": [],
        "spanish": [],
        "german": []
    }

    # Universal queries (with EAN)
    if ean:
        queries["universal"].append(f"{ean} amazon")
        queries["universal"].append(f"{ean} product")

    # Brand + Model queries in multiple languages
    if brand and model:
        # French
        queries["french"].append(f"{brand} {model} fiche technique")
        queries["french"].append(f"{brand} {model} amazon")

        # English
        queries["english"].append(f"{brand} {model} specifications")
        queries["english"].append(f"{brand} {model} amazon")

        # Italian
        queries["italian"].append(f"{brand} {model} scheda tecnica")
        queries["italian"].append(f"{brand} {model} amazon")

        # Spanish
        queries["spanish"].append(f"{brand} {model} especificaciones")
        queries["spanish"].append(f"{brand} {model} amazon")

        # German
        queries["german"].append(f"{brand} {model} technische daten")
        queries["german"].append(f"{brand} {model} amazon")

    # Supplier reference queries
    if reference:
        queries["universal"].append(f"{reference} {brand}")
        queries["english"].append(f"{reference} datasheet")

    return queries


def get_today_str() -> str:
    """Get today's date as a string."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


# Think tool (for strategic reflection)
@tool
def think_tool(reflection: str) -> str:
    """
    Pause for strategic reflection and planning.

    Use this tool to think through your search strategy before making decisions.

    Args:
        reflection: Your strategic thoughts and plans

    Returns:
        Confirmation that reflection was recorded
    """
    return f"Reflection recorded: {reflection[:100]}..."
