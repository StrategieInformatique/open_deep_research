"""Configuration for the Article Enrichment system.

This module defines the configuration options for the cascade enrichment process.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class SearchAPI(str, Enum):
    """Available search API providers."""
    TAVILY = "tavily"
    # Future: Add other search providers if needed


class EnrichmentType(str, Enum):
    """Types of enrichment strategies."""
    REFERENTIEL = "REFERENTIEL"  # Amazon-based enrichment
    WEB = "WEB"  # Multi-source web enrichment
    GENERATIF = "GENERATIF"  # AI-native generation
    EN_ATTENTE = "EN_ATTENTE"  # Pending - missing data


class EnrichmentStatus(str, Enum):
    """Status of enrichment processing."""
    COMPLETE = "COMPLETE"
    EN_ATTENTE = "EN_ATTENTE"
    EN_COURS = "EN_COURS"
    REJECTED = "REJECTED"


class AmazonDomains(BaseModel):
    """Configuration for Amazon domains to search."""
    domains: List[str] = Field(
        default=[
            "amazon.fr",
            "amazon.it",
            "amazon.com",
            "amazon.es",
            "amazon.de",
            "amazon.co.uk"
        ],
        description="List of Amazon domains to search across"
    )


class SearchLanguages(BaseModel):
    """Languages to use for multi-language searches."""
    languages: List[str] = Field(
        default=["french", "english", "italian", "spanish", "german"],
        description="Languages to formulate search queries in"
    )

    language_codes: dict = Field(
        default={
            "french": "fr",
            "english": "en",
            "italian": "it",
            "spanish": "es",
            "german": "de"
        },
        description="Mapping of language names to ISO codes"
    )


class ScoringThresholds(BaseModel):
    """Confidence score thresholds for routing decisions."""

    # Minimum confidence scores for each enrichment type
    referentiel_min: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score to route to REFERENTIEL (Amazon)"
    )

    web_min: float = Field(
        default=0.60,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score to route to WEB enrichment"
    )

    generatif_min: float = Field(
        default=0.50,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score for GENERATIF enrichment"
    )

    # Scoring weights for matching criteria
    ean_match_weight: float = Field(default=0.40, description="Weight for EAN match")
    brand_match_weight: float = Field(default=0.25, description="Weight for brand match")
    model_match_weight: float = Field(default=0.25, description="Weight for model match")
    category_match_weight: float = Field(default=0.10, description="Weight for category match")

    # Web search thresholds
    min_web_sources: int = Field(
        default=2,
        ge=1,
        description="Minimum number of relevant web sources for WEB enrichment"
    )

    tavily_relevance_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum Tavily relevance score to consider a source"
    )


class EnrichmentConfiguration(BaseModel):
    """Main configuration for the Article Enrichment system."""

    # =========================================================================
    # GENERAL SETTINGS
    # =========================================================================

    max_structured_output_retries: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retries for structured output generation"
    )

    # =========================================================================
    # SEARCH CONFIGURATION
    # =========================================================================

    search_api: SearchAPI = Field(
        default=SearchAPI.TAVILY,
        description="Search API provider to use"
    )

    amazon_domains: AmazonDomains = Field(
        default_factory=AmazonDomains,
        description="Amazon domains configuration"
    )

    search_languages: SearchLanguages = Field(
        default_factory=SearchLanguages,
        description="Languages for multi-language searches"
    )

    # =========================================================================
    # DEEP RESEARCHER SETTINGS
    # =========================================================================

    max_search_iterations: int = Field(
        default=8,
        ge=3,
        le=20,
        description="Maximum number of search tool calls for deep_researcher"
    )

    max_amazon_searches: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum searches for Amazon phase"
    )

    max_web_searches: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum searches for general web phase"
    )

    max_technical_searches: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Maximum searches for technical documentation phase"
    )

    tavily_search_depth: str = Field(
        default="advanced",
        description="Tavily search depth: 'basic' (1 credit) or 'advanced' (2 credits)"
    )

    tavily_max_results: int = Field(
        default=10,
        ge=1,
        le=20,
        description="Maximum results per Tavily search"
    )

    # =========================================================================
    # SCORING AND MATCHING
    # =========================================================================

    scoring_thresholds: ScoringThresholds = Field(
        default_factory=ScoringThresholds,
        description="Confidence score thresholds and weights"
    )

    # =========================================================================
    # MODEL CONFIGURATION
    # =========================================================================

    # Deep Researcher model (most important - needs strong reasoning)
    deep_researcher_model: str = Field(
        default="openai:gpt-4o",
        description="Model for deep_researcher (searches + routing decisions)"
    )

    # Brief generation model (can be lighter)
    brief_generation_model: str = Field(
        default="openai:gpt-4o-mini",
        description="Model for transforming article payload to research brief"
    )

    # Report generation model (needs quality writing)
    report_generation_model: str = Field(
        default="openai:gpt-4o",
        description="Model for generating enrichment reports"
    )

    # Subgraph models (specialized tasks)
    amazon_enrichment_model: str = Field(
        default="openai:gpt-4o",
        description="Model for REFERENTIEL (Amazon) subgraph"
    )

    web_enrichment_model: str = Field(
        default="openai:gpt-4o",
        description="Model for WEB enrichment subgraph"
    )

    generative_enrichment_model: str = Field(
        default="openai:gpt-4o",
        description="Model for GENERATIF enrichment subgraph"
    )

    # =========================================================================
    # EXTRACTION SETTINGS
    # =========================================================================

    tavily_extract_depth: str = Field(
        default="advanced",
        description="Tavily extract depth: 'basic' or 'advanced'"
    )

    tavily_extract_timeout: int = Field(
        default=30,
        ge=10,
        le=60,
        description="Timeout in seconds for Tavily extraction"
    )

    # =========================================================================
    # GENERATIF PRE-REQUISITES
    # =========================================================================

    generatif_requires_image: bool = Field(
        default=True,
        description="Whether GENERATIF enrichment requires at least one image"
    )

    generatif_requires_technical_data: bool = Field(
        default=True,
        description="Whether GENERATIF enrichment requires technical data or PDF"
    )

    # =========================================================================
    # OUTPUT SETTINGS
    # =========================================================================

    output_language: str = Field(
        default="french",
        description="Language for enriched content (always French for now)"
    )

    include_search_metadata: bool = Field(
        default=True,
        description="Include search metadata in enrichment report"
    )

    include_confidence_details: bool = Field(
        default=True,
        description="Include detailed confidence scoring in report"
    )


# =============================================================================
# DEFAULT CONFIGURATION INSTANCE
# =============================================================================

def get_default_enrichment_config() -> EnrichmentConfiguration:
    """Get the default enrichment configuration."""
    return EnrichmentConfiguration()


# =============================================================================
# CONFIGURATION HELPERS
# =============================================================================

def get_amazon_domain_list() -> List[str]:
    """Get list of Amazon domains to search."""
    config = get_default_enrichment_config()
    return config.amazon_domains.domains


def get_search_languages_list() -> List[str]:
    """Get list of languages for multi-language search."""
    config = get_default_enrichment_config()
    return config.search_languages.languages


def calculate_matching_score(
    ean_match: bool,
    brand_match: bool,
    model_match: bool,
    category_match: bool,
    config: Optional[EnrichmentConfiguration] = None
) -> float:
    """
    Calculate a matching confidence score based on matching criteria.

    Args:
        ean_match: Whether EAN matches
        brand_match: Whether brand matches
        model_match: Whether model/reference matches
        category_match: Whether product category matches
        config: Optional configuration (uses default if None)

    Returns:
        Confidence score between 0.0 and 1.0
    """
    if config is None:
        config = get_default_enrichment_config()

    thresholds = config.scoring_thresholds

    score = 0.0
    if ean_match:
        score += thresholds.ean_match_weight
    if brand_match:
        score += thresholds.brand_match_weight
    if model_match:
        score += thresholds.model_match_weight
    if category_match:
        score += thresholds.category_match_weight

    return min(score, 1.0)  # Cap at 1.0


def should_route_to_referentiel(confidence_score: float, config: Optional[EnrichmentConfiguration] = None) -> bool:
    """
    Determine if confidence score is sufficient for REFERENTIEL routing.

    Args:
        confidence_score: Calculated confidence score
        config: Optional configuration (uses default if None)

    Returns:
        True if should route to REFERENTIEL, False otherwise
    """
    if config is None:
        config = get_default_enrichment_config()

    return confidence_score >= config.scoring_thresholds.referentiel_min


def should_route_to_web(confidence_score: float, num_sources: int, config: Optional[EnrichmentConfiguration] = None) -> bool:
    """
    Determine if should route to WEB enrichment.

    Args:
        confidence_score: Calculated confidence score
        num_sources: Number of relevant web sources found
        config: Optional configuration (uses default if None)

    Returns:
        True if should route to WEB, False otherwise
    """
    if config is None:
        config = get_default_enrichment_config()

    thresholds = config.scoring_thresholds
    return (
        confidence_score >= thresholds.web_min and
        num_sources >= thresholds.min_web_sources
    )
