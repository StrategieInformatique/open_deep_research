"""Configuration centralisée du logging pour Article Enrichment."""

import logging
import os
import sys
from typing import Optional

# Détection de l'environnement
IS_LOCAL_DEV = "langgraph dev" in ' '.join(sys.argv) or os.getenv("LANGGRAPH_ENV") == "local"

def setup_logger(name: str = "enrichment", level: Optional[str] = None) -> logging.Logger:
    """
    Configure un logger pour l'application d'enrichissement.

    Args:
        name: Nom du logger
        level: Niveau de log (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)

    # Utiliser le niveau depuis l'env ou par défaut INFO
    log_level = level or os.getenv("LOG_LEVEL", "INFO")
    logger.setLevel(getattr(logging, log_level))

    # Ne pas propager pour éviter les doublons avec les loggers LangGraph
    logger.propagate = False

    # Éviter les doublons de handlers
    if not logger.handlers:
        # Handler console avec format clair et encodage UTF-8
        handler = logging.StreamHandler()

        # Forcer l'encodage UTF-8
        if hasattr(handler.stream, 'reconfigure'):
            handler.stream.reconfigure(encoding='utf-8')

        # Format différent pour local vs production
        if IS_LOCAL_DEV:
            # Format simple et lisible pour développement local
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
        else:
            # Format pour production (sera capturé par LangGraph Platform)
            formatter = logging.Formatter(
                '%(levelname)s - %(name)s - %(message)s'
            )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Réduire le bruit des loggers tiers en local
    if IS_LOCAL_DEV:
        configure_third_party_loggers()

    return logger


def configure_third_party_loggers():
    """Réduit le niveau de log des bibliothèques tierces en développement local."""
    third_party_loggers = [
        "langgraph_runtime_inmem",
        "langgraph_api",
        "langsmith",
        "urllib3",
        "httpx",
        "httpcore",
        "tavily"
    ]

    for logger_name in third_party_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)


# Créer des loggers spécialisés
def get_enrichment_logger() -> logging.Logger:
    """Obtient le logger principal pour l'enrichissement."""
    return setup_logger("enrichment")


def get_deep_researcher_logger() -> logging.Logger:
    """Obtient un logger pour le deep_researcher node."""
    return setup_logger("deep_researcher")


def get_subgraph_logger(subgraph_name: str) -> logging.Logger:
    """Obtient un logger spécifique pour un subgraph."""
    return setup_logger(f"subgraph_{subgraph_name}")


def get_tavily_logger() -> logging.Logger:
    """Obtient un logger pour les appels Tavily."""
    return setup_logger("tavily_api")
