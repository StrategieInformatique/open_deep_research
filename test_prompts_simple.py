"""
Script de test SIMPLE pour tester les prompts d'enrichissement.

PAS de LangGraph, juste les prompts et Tavily.
"""

import asyncio
import os
import sys
from datetime import datetime

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from open_deep_research.configuration_enrichment import EnrichmentConfiguration
from open_deep_research.utils_enrichment import (
    format_article_for_search,
    extract_asin_from_url,
    extract_domain_from_url,
)


# =============================================================================
# ARTICLE DE TEST (Centrale Vapeur BRAUN)
# =============================================================================

ARTICLE_TEST = {
    "article_id": "DELO-IS2144BK",
    "libelle": "CENTRALE VAPEUR IS2144BK NOIR BRAUN",
    "marque": "BRAUN",
    "ean": "8021098280152",
    "reference_fournisseur": "IS2144BK",
    "famille_produit": "CENTRALE VAPEUR",
    "images_disponibles": True,
    "images_urls": ["https://example.com/image.jpg"],
    "specifications_techniques": {
        "couleur": "Noir",
        "prix_ttc": 179.99
    }
}


# =============================================================================
# FONCTION DE RECHERCHE TAVILY (Simple)
# =============================================================================

async def search_amazon_simple(queries, max_results=10):
    """Recherche simple sur Amazon avec Tavily."""
    try:
        from tavily import TavilyClient
    except ImportError:
        print("❌ Tavily non installé. Installez avec: pip install tavily-python")
        return []

    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        print("❌ TAVILY_API_KEY non défini")
        return []

    client = TavilyClient(api_key=api_key)

    amazon_domains = [
        "amazon.fr",
        "amazon.it",
        "amazon.com",
        "amazon.es",
        "amazon.de",
        "amazon.co.uk"
    ]

    all_results = []

    print(f"\n🔍 Recherche Amazon avec {len(queries)} requête(s)...")
    for idx, query in enumerate(queries, 1):
        print(f"  {idx}. Requête: {query}")

        try:
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=amazon_domains
            )

            results = response.get("results", [])
            print(f"     ✅ {len(results)} résultat(s) trouvé(s)")

            for result in results:
                url = result.get("url", "")
                asin = extract_asin_from_url(url)
                domain = extract_domain_from_url(url)

                if asin and domain:
                    all_results.append({
                        "query": query,
                        "url": url,
                        "asin": asin,
                        "domain": domain,
                        "title": result.get("title", ""),
                        "score": result.get("score", 0.0),
                        "content": result.get("content", "")[:200]
                    })

        except Exception as e:
            print(f"     ❌ Erreur: {str(e)}")

    return all_results


async def search_web_simple(queries, max_results=10):
    """Recherche simple sur le web avec Tavily."""
    try:
        from tavily import TavilyClient
    except ImportError:
        print("❌ Tavily non installé")
        return []

    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        print("❌ TAVILY_API_KEY non défini")
        return []

    client = TavilyClient(api_key=api_key)

    all_results = []

    print(f"\n🌐 Recherche Web avec {len(queries)} requête(s)...")
    for idx, query in enumerate(queries, 1):
        print(f"  {idx}. Requête: {query}")

        try:
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results
            )

            results = response.get("results", [])
            print(f"     ✅ {len(results)} résultat(s) trouvé(s)")

            for result in results:
                url = result.get("url", "")
                domain = extract_domain_from_url(url)
                score = result.get("score", 0.0)

                if score >= 0.5:  # Seuil de pertinence
                    all_results.append({
                        "query": query,
                        "url": url,
                        "domain": domain,
                        "title": result.get("title", ""),
                        "score": score,
                        "content": result.get("content", "")[:200]
                    })

        except Exception as e:
            print(f"     ❌ Erreur: {str(e)}")

    return all_results


# =============================================================================
# TEST PRINCIPAL
# =============================================================================

async def test_enrichment_prompts():
    """Test des prompts d'enrichissement."""

    print("="*80)
    print("🧪 TEST DES PROMPTS D'ENRICHISSEMENT")
    print("="*80)

    # Configuration
    config = EnrichmentConfiguration()

    # Article à tester
    article = ARTICLE_TEST
    print(f"\n📦 Article: {article['marque']} {article['libelle']}")
    print(f"   EAN: {article['ean']}")
    print(f"   Réf: {article['reference_fournisseur']}")

    # Génération des requêtes multilingues
    print("\n" + "="*80)
    print("📝 GÉNÉRATION DES REQUÊTES MULTILINGUES")
    print("="*80)

    queries = format_article_for_search(article)

    for lang, lang_queries in queries.items():
        if lang_queries:
            print(f"\n{lang.upper()}:")
            for q in lang_queries:
                print(f"  - {q}")

    # Phase 1 : Recherche Amazon
    print("\n" + "="*80)
    print("🛒 PHASE 1 : RECHERCHE AMAZON")
    print("="*80)

    amazon_queries = []
    if queries.get("universal"):
        amazon_queries.extend(queries["universal"])
    if queries.get("english"):
        amazon_queries.extend(queries["english"][:2])
    if queries.get("french"):
        amazon_queries.extend(queries["french"][:1])

    amazon_queries = amazon_queries[:config.max_amazon_searches]

    amazon_results = await search_amazon_simple(amazon_queries, config.tavily_max_results)

    print(f"\n📊 RÉSULTATS AMAZON : {len(amazon_results)} produit(s)")
    for idx, result in enumerate(amazon_results, 1):
        print(f"\n  {idx}. {result['title'][:80]}")
        print(f"     ASIN: {result['asin']}")
        print(f"     Domain: {result['domain']}")
        print(f"     URL: {result['url']}")
        print(f"     Score: {result['score']:.2f}")

    # Décision Phase 1
    if amazon_results:
        print(f"\n✅ DÉCISION : REFERENTIEL (Amazon trouvé)")
        print(f"   → {len(amazon_results)} produit(s) Amazon trouvé(s)")
        print(f"   → Prochain step : amazon_subgraph")
        return "REFERENTIEL", amazon_results

    print(f"\n❌ Aucun produit Amazon trouvé, passage à Phase 2...")

    # Phase 2 : Recherche Web
    print("\n" + "="*80)
    print("🌐 PHASE 2 : RECHERCHE WEB")
    print("="*80)

    web_queries = []
    if queries.get("english"):
        web_queries.extend(queries["english"][:2])
    if queries.get("french"):
        web_queries.extend(queries["french"][:1])
    if queries.get("italian"):
        web_queries.extend(queries["italian"][:1])

    web_queries = web_queries[:config.max_web_searches]

    web_results = await search_web_simple(web_queries, config.tavily_max_results)

    print(f"\n📊 RÉSULTATS WEB : {len(web_results)} source(s)")
    for idx, result in enumerate(web_results, 1):
        print(f"\n  {idx}. {result['title'][:80]}")
        print(f"     Domain: {result['domain']}")
        print(f"     URL: {result['url']}")
        print(f"     Score: {result['score']:.2f}")

    # Décision Phase 2
    if len(web_results) >= config.scoring_thresholds.min_web_sources:
        print(f"\n✅ DÉCISION : WEB (Sources web trouvées)")
        print(f"   → {len(web_results)} source(s) web trouvée(s)")
        print(f"   → Prochain step : web_subgraph")
        return "WEB", web_results

    print(f"\n❌ Seulement {len(web_results)} source(s) (min: {config.scoring_thresholds.min_web_sources})")

    # Phase 3 : Vérification GENERATIF
    print("\n" + "="*80)
    print("✨ PHASE 3 : VÉRIFICATION GENERATIF")
    print("="*80)

    has_images = article.get("images_disponibles", False)
    has_tech_data = bool(article.get("specifications_techniques") or article.get("fiche_technique_url"))

    print(f"  Images disponibles: {'✅' if has_images else '❌'}")
    print(f"  Données techniques: {'✅' if has_tech_data else '❌'}")

    if has_images and has_tech_data:
        print(f"\n✅ DÉCISION : GENERATIF (Données disponibles)")
        print(f"   → Prochain step : generative_subgraph")
        return "GENERATIF", {"images": has_images, "tech_data": has_tech_data}

    # Fallback : EN_ATTENTE
    print("\n" + "="*80)
    print("⏳ DÉCISION FINALE : EN_ATTENTE")
    print("="*80)

    missing = []
    if not has_images:
        missing.append("Images produit")
    if not has_tech_data:
        missing.append("Données techniques")

    print(f"  Données manquantes:")
    for item in missing:
        print(f"    - {item}")

    return "EN_ATTENTE", {"missing_data": missing}


# =============================================================================
# MAIN
# =============================================================================

async def main():
    """Point d'entrée principal."""

    # Vérifier les variables d'environnement
    if not os.environ.get("TAVILY_API_KEY"):
        print("\n❌ ERREUR : TAVILY_API_KEY non défini")
        print("Définissez-le avec : export TAVILY_API_KEY='tvly-votre-clé'")
        return

    start_time = datetime.now()

    try:
        decision, data = await test_enrichment_prompts()
    except Exception as e:
        print(f"\n❌ ERREUR : {str(e)}")
        import traceback
        traceback.print_exc()
        return

    duration = (datetime.now() - start_time).total_seconds()

    # Résumé final
    print("\n" + "="*80)
    print("✅ TEST TERMINÉ")
    print("="*80)
    print(f"  Type d'enrichissement: {decision}")
    print(f"  Durée: {duration:.2f}s")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
