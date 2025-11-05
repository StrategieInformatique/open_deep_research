"""Example script to test the Article Enrichment workflow.

This script demonstrates how to:
1. Create an article payload
2. Run the enrichment graph
3. View the search results and routing decision
"""

import asyncio
from datetime import datetime

from open_deep_research.article_enrichment_graph import enrichment_graph
from open_deep_research.state_enrichment import (
    ArticlePayload,
    create_initial_enrichment_state,
)


# =============================================================================
# EXAMPLE ARTICLES FOR TESTING
# =============================================================================

# Example 1: Product likely available on Amazon
ARTICLE_AMAZON_EXAMPLE = ArticlePayload(
    article_id="TEST001",
    libelle="MacBook Pro 14 pouces",
    marque="Apple",
    ean="0194252721124",  # Real MacBook Pro EAN
    reference_fournisseur="MK1E3FN/A",
    famille_produit="Informatique > Ordinateurs portables",
    images_disponibles=False,
    specifications_techniques=None,
)

# Example 2: Product NOT on Amazon but available on web
ARTICLE_WEB_EXAMPLE = ArticlePayload(
    article_id="TEST002",
    libelle="Centrale vapeur Pro Express",
    marque="Calor",
    ean=None,
    reference_fournisseur="GV9580C0",
    famille_produit="Électroménager > Repassage",
    images_disponibles=False,
    specifications_techniques=None,
)

# Example 3: Product with images and technical data (GENERATIF candidate)
ARTICLE_GENERATIF_EXAMPLE = ArticlePayload(
    article_id="TEST003",
    libelle="Pompe hydraulique industrielle XZ-2000",
    marque="HydroTech",
    ean=None,
    reference_fournisseur="HT-XZ2000-EU",
    famille_produit="Équipement industriel > Pompes",
    images_disponibles=True,
    images_urls=[
        "https://example.com/images/ht-xz2000-1.jpg",
        "https://example.com/images/ht-xz2000-2.jpg",
    ],
    fiche_technique_url="https://example.com/datasheets/ht-xz2000.pdf",
    specifications_techniques={
        "puissance": "2000W",
        "debit": "120 L/min",
        "pression": "10 bar",
    },
)

# Example 4: Product with missing data (EN_ATTENTE)
ARTICLE_PENDING_EXAMPLE = ArticlePayload(
    article_id="TEST004",
    libelle="Widget mystérieux",
    marque="InconnuCorp",
    ean=None,
    reference_fournisseur="UNKN-001",
    famille_produit="Divers",
    images_disponibles=False,
    specifications_techniques=None,
)


# =============================================================================
# TEST FUNCTION
# =============================================================================

async def test_enrichment(article: ArticlePayload):
    """
    Test the enrichment workflow with an article.

    Args:
        article: Article payload to enrich
    """
    print("\n" + "="*80)
    print(f"🧪 TESTING ENRICHMENT FOR: {article.marque} {article.libelle}")
    print("="*80)

    # Create initial state
    initial_state = create_initial_enrichment_state(article)

    # Run the graph
    print("\n🚀 Starting enrichment workflow...\n")

    try:
        final_state = await enrichment_graph.ainvoke(
            initial_state,
            config={
                "configurable": {
                    "model": "openai:gpt-4o-mini",  # Use cheaper model for testing
                }
            }
        )

        print("\n✅ Enrichment workflow completed!")

        # Display final state summary
        routing = final_state.get("routing_decision")
        if routing:
            print(f"\n📋 Final State Summary:")
            print(f"   Enrichment Type: {routing.enrichment_type}")
            print(f"   Confidence: {routing.confidence_score:.2f}")
            print(f"   Status: {final_state.get('enrichment_status', 'N/A')}")

    except Exception as e:
        print(f"\n❌ Error during enrichment: {e}")
        import traceback
        traceback.print_exc()


# =============================================================================
# MAIN
# =============================================================================

async def main():
    """Run enrichment tests on example articles."""

    print("\n" + "="*80)
    print("📦 ARTICLE ENRICHMENT - TEST SUITE")
    print("="*80)

    # Test 1: Amazon example
    print("\n\n📍 TEST 1: Product likely on Amazon")
    await test_enrichment(ARTICLE_AMAZON_EXAMPLE)

    # Uncomment to test other examples:

    # # Test 2: Web example
    # print("\n\n📍 TEST 2: Product likely on web (not Amazon)")
    # await test_enrichment(ARTICLE_WEB_EXAMPLE)

    # # Test 3: Generative example
    # print("\n\n📍 TEST 3: Product for generative enrichment")
    # await test_enrichment(ARTICLE_GENERATIF_EXAMPLE)

    # # Test 4: Pending example
    # print("\n\n📍 TEST 4: Product with missing data")
    # await test_enrichment(ARTICLE_PENDING_EXAMPLE)

    print("\n\n" + "="*80)
    print("✅ ALL TESTS COMPLETED")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Check for required environment variables
    import os

    if not os.environ.get("TAVILY_API_KEY"):
        print("❌ ERROR: TAVILY_API_KEY environment variable not set")
        print("Please set it with: export TAVILY_API_KEY='your-key-here'")
        exit(1)

    if not os.environ.get("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY='your-key-here'")
        exit(1)

    # Run tests
    asyncio.run(main())
