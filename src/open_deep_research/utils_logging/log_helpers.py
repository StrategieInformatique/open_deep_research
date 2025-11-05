"""Helpers pour améliorer la structure et la lisibilité des logs pour l'enrichissement."""

from typing import Dict, Any, Optional, List
from open_deep_research.state_enrichment import (
    EnrichmentState,
    AmazonProduct,
    WebSource,
    RoutingDecision,
)


def log_separator(logger, char="=", length=80):
    """Log un séparateur visuel."""
    logger.info(char * length)


def log_node_entry(logger, node_name: str, state: Optional[EnrichmentState] = None):
    """Log l'entrée dans un node."""
    log_separator(logger)
    logger.info(f"🔵 [NODE_ENTRY] {node_name}")
    if state:
        article = state.get("article_payload")
        if article:
            logger.info(f"  📦 Article: {article.marque} {article.libelle}")
            if article.ean:
                logger.info(f"  🔢 EAN: {article.ean}")
    log_separator(logger)


def log_node_exit(logger, node_name: str, next_node: Optional[str] = None):
    """Log la sortie d'un node."""
    logger.info(f"✅ [NODE_EXIT] {node_name}")
    if next_node:
        logger.info(f"  ➡️  Next: {next_node}")
    log_separator(logger)


def log_article_info(logger, state: EnrichmentState):
    """Log les informations de l'article de manière structurée."""
    log_separator(logger)
    logger.info("[ARTICLE_INFO] Informations produit")

    article = state["article_payload"]

    # Données principales
    logger.info(f"  📦 Produit: {article.libelle}")
    logger.info(f"  🏷️  Marque: {article.marque}")

    if article.ean:
        logger.info(f"  🔢 EAN: {article.ean}")

    if article.reference_fournisseur:
        logger.info(f"  📋 Réf Fournisseur: {article.reference_fournisseur}")

    if article.famille_produit:
        logger.info(f"  📂 Catégorie: {article.famille_produit}")

    # Données enrichissement
    if article.images_disponibles:
        nb_images = len(article.images_urls) if article.images_urls else 0
        logger.info(f"  🖼️  Images: ✅ ({nb_images})")
    else:
        logger.info(f"  🖼️  Images: ❌")

    if article.specifications_techniques:
        logger.info(f"  ⚙️  Specs techniques: ✅")
    else:
        logger.info(f"  ⚙️  Specs techniques: ❌")

    if article.fiche_technique_url:
        logger.info(f"  📄 Fiche technique: ✅")

    log_separator(logger)


def log_search_phase(logger, phase_number: int, phase_name: str, queries: List[str]):
    """Log le début d'une phase de recherche."""
    log_separator(logger, char="-")
    logger.info(f"🔍 [PHASE {phase_number}] {phase_name}")
    logger.info(f"  📝 Nombre de requêtes: {len(queries)}")
    for idx, query in enumerate(queries[:3], 1):  # Afficher max 3 requêtes
        logger.info(f"    {idx}. {query}")
    if len(queries) > 3:
        logger.info(f"    ... et {len(queries) - 3} autres")
    log_separator(logger, char="-")


def log_amazon_results(logger, products: List[AmazonProduct]):
    """Log les résultats de recherche Amazon."""
    if not products:
        logger.info("  ❌ Aucun produit Amazon trouvé")
        return

    logger.info(f"  ✅ {len(products)} produit(s) Amazon trouvé(s)")
    for idx, product in enumerate(products, 1):
        logger.info(f"    {idx}. ASIN: {product.asin}")
        logger.info(f"       Domain: {product.domain}")
        logger.info(f"       URL: {product.url}")
        if product.title:
            logger.info(f"       Title: {product.title[:60]}...")


def log_web_results(logger, sources: List[WebSource]):
    """Log les résultats de recherche web."""
    if not sources:
        logger.info("  ❌ Aucune source web trouvée")
        return

    logger.info(f"  ✅ {len(sources)} source(s) web trouvée(s)")
    for idx, source in enumerate(sources, 1):
        logger.info(f"    {idx}. Domain: {source.domain}")
        logger.info(f"       Score: {source.relevance_score:.2f}")
        logger.info(f"       URL: {source.url}")
        if source.title:
            logger.info(f"       Title: {source.title[:60]}...")


def log_routing_decision(logger, decision: RoutingDecision):
    """Log la décision de routage."""
    log_separator(logger)
    logger.info("🎯 [ROUTING_DECISION] Décision de routage")
    logger.info(f"  📍 Type d'enrichissement: {decision.enrichment_type}")
    logger.info(f"  📊 Score de confiance: {decision.confidence_score:.2f}")
    logger.info(f"  📝 Justification: {decision.justification}")

    # Détails selon le type
    if decision.enrichment_type == "REFERENTIEL" and decision.amazon_data:
        logger.info(f"  🛒 Produits Amazon: {len(decision.amazon_data)}")
        for product in decision.amazon_data[:2]:  # Max 2
            logger.info(f"     • ASIN: {product.asin} ({product.domain})")

    elif decision.enrichment_type == "WEB" and decision.web_sources:
        logger.info(f"  🌐 Sources web: {len(decision.web_sources)}")
        for source in decision.web_sources[:2]:  # Max 2
            logger.info(f"     • {source.domain} (score: {source.relevance_score:.2f})")

    elif decision.enrichment_type == "GENERATIF" and decision.generatif_data:
        data = decision.generatif_data
        if data.get('images'):
            logger.info(f"  🖼️  Images: {len(data['images'])}")
        if data.get('technical_specs'):
            logger.info(f"  ⚙️  Specs techniques: Oui")
        if data.get('datasheet_url'):
            logger.info(f"  📄 Fiche technique: Oui")

    elif decision.enrichment_type == "EN_ATTENTE" and decision.missing_data:
        logger.info(f"  ⏳ Données manquantes:")
        for item in decision.missing_data:
            logger.info(f"     • {item}")

    # Résumé de recherche
    if decision.search_summary:
        summary = decision.search_summary
        logger.info(f"  🔍 Résumé recherche:")
        logger.info(f"     • Phase: {summary.get('phase', 'N/A')}")
        logger.info(f"     • Requêtes: {summary.get('queries_count', 0)}")
        logger.info(f"     • Résultats: {summary.get('results_count', 0)}")
        if summary.get('languages'):
            logger.info(f"     • Langues: {', '.join(summary['languages'])}")

    log_separator(logger)


def log_tavily_call(logger, tool_name: str, queries: List[str], results_count: int, success: bool = True):
    """Log un appel à Tavily."""
    status = "✅" if success else "❌"
    logger.info(f"[TAVILY_CALL] {status} {tool_name}")
    logger.info(f"  • Requêtes: {len(queries)}")
    logger.info(f"  • Résultats: {results_count}")
    if not success:
        logger.info(f"  • Status: FAILED")


def log_confidence_calculation(logger, ean_match: bool, brand_match: bool, model_match: bool, category_match: bool, final_score: float):
    """Log le calcul du score de confiance."""
    logger.info("📊 [CONFIDENCE_CALC] Calcul du score de confiance")
    logger.info(f"  • EAN match: {'✅' if ean_match else '❌'}")
    logger.info(f"  • Brand match: {'✅' if brand_match else '❌'}")
    logger.info(f"  • Model match: {'✅' if model_match else '❌'}")
    logger.info(f"  • Category match: {'✅' if category_match else '❌'}")
    logger.info(f"  • Score final: {final_score:.2f}")


def log_error(logger, node_name: str, error_msg: str, context: Optional[Dict[str, Any]] = None):
    """Log structuré pour les erreurs."""
    log_separator(logger)
    logger.error(f"❌ [ERROR] Erreur dans {node_name}")
    logger.error(f"  Message: {error_msg}")

    if context:
        logger.error("  Contexte:")
        for key, value in context.items():
            logger.error(f"    • {key}: {value}")

    log_separator(logger)


def log_processing_time(logger, node_name: str, duration_seconds: float):
    """Log le temps de traitement d'un node."""
    logger.info(f"⏱️  [TIMING] {node_name}: {duration_seconds:.2f}s")


def log_final_summary(logger, state: EnrichmentState):
    """Log le résumé final du traitement."""
    log_separator(logger, char="=")
    logger.info("📋 [FINAL_SUMMARY] Résumé du traitement")

    routing = state.get("routing_decision")
    if routing:
        logger.info(f"  🎯 Type: {routing.enrichment_type}")
        logger.info(f"  📊 Confiance: {routing.confidence_score:.2f}")

    status = state.get("enrichment_status", "N/A")
    logger.info(f"  📌 Statut: {status}")

    if state.get("processing_start_time") and state.get("processing_end_time"):
        from datetime import datetime
        start = state["processing_start_time"]
        end = state["processing_end_time"]
        if isinstance(start, datetime) and isinstance(end, datetime):
            duration = (end - start).total_seconds()
            logger.info(f"  ⏱️  Durée totale: {duration:.2f}s")

    iterations = state.get("search_iterations_count", 0)
    if iterations:
        logger.info(f"  🔄 Itérations de recherche: {iterations}")

    log_separator(logger, char="=")
