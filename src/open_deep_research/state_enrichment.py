"""State definitions for the Article Enrichment system.

This module defines all state classes and structured outputs used in the
cascade enrichment workflow.
"""

from typing import Annotated, List, Literal, Optional, Dict, Any
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState
import datetime


# =============================================================================
# STRUCTURED OUTPUTS (for .with_structured_output())
# =============================================================================

class ArticlePayload(BaseModel):
    """Input article payload with product information."""

    # Required fields
    article_id: str = Field(description="Unique article identifier")
    libelle: str = Field(description="Product label/name")
    marque: str = Field(description="Product brand")

    # Optional identifiers
    ean: Optional[str] = Field(default=None, description="EAN/UPC/GTIN code")
    reference_fournisseur: Optional[str] = Field(default=None, description="Supplier reference")

    # Optional product data
    famille_produit: Optional[str] = Field(default=None, description="Product family/category")
    specifications_techniques: Optional[Dict[str, Any]] = Field(default=None, description="Technical specifications")

    # Media and documentation
    images_disponibles: bool = Field(default=False, description="Whether product images are available")
    images_urls: Optional[List[str]] = Field(default=None, description="List of image URLs")
    fiche_technique_url: Optional[str] = Field(default=None, description="URL to technical datasheet PDF")
    documents_techniques: Optional[List[str]] = Field(default=None, description="URLs to technical documents")

    # Metadata
    date_creation: Optional[str] = Field(default=None, description="Creation date")
    derniere_modification: Optional[str] = Field(default=None, description="Last modification date")


class ResearchBrief(BaseModel):
    """Structured research brief for product enrichment."""

    # Product identity
    product_identity: Dict[str, Any] = Field(
        description="Structured product identity (EAN, brand, model, category)"
    )

    # Multi-language search queries
    search_queries: Dict[str, List[str]] = Field(
        description="Search queries organized by language (french, english, italian, spanish, german)"
    )

    # Search strategy
    search_strategy: Dict[str, Any] = Field(
        description="Search strategy including priorities and target domains"
    )

    # Success criteria
    success_criteria: Dict[str, Any] = Field(
        description="Matching criteria and minimum data quality requirements"
    )


class AmazonProduct(BaseModel):
    """Amazon product information found during search."""

    asin: str = Field(description="Amazon Standard Identification Number (10 characters)")
    domain: str = Field(description="Amazon domain (e.g., amazon.fr, amazon.com)")
    url: str = Field(description="Full product URL")
    title: Optional[str] = Field(default=None, description="Product title on Amazon")
    price: Optional[str] = Field(default=None, description="Product price")
    rating: Optional[float] = Field(default=None, description="Product rating")
    reviews_count: Optional[int] = Field(default=None, description="Number of reviews")
    availability: Optional[str] = Field(default=None, description="Availability status")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata from search")


class WebSource(BaseModel):
    """Web source found during general web search."""

    url: str = Field(description="URL of the source")
    title: Optional[str] = Field(default=None, description="Page title")
    domain: str = Field(description="Domain name")
    content_snippet: Optional[str] = Field(default=None, description="Content snippet from search")
    relevance_score: float = Field(description="Tavily relevance score (0.0-1.0)")
    language: Optional[str] = Field(default=None, description="Detected language of content")
    source_type: Optional[str] = Field(
        default=None,
        description="Type of source (manufacturer, retailer, spec_database, etc.)"
    )
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class TechnicalDocument(BaseModel):
    """Technical documentation found during search."""

    url: str = Field(description="URL of the technical document")
    document_type: str = Field(description="Type: PDF, webpage, etc.")
    title: Optional[str] = Field(default=None, description="Document title")
    content_extracted: Optional[str] = Field(default=None, description="Extracted content")
    specifications_found: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Technical specifications extracted"
    )
    language: Optional[str] = Field(default=None, description="Document language")


class RoutingDecision(BaseModel):
    """Routing decision made by deep_researcher."""

    enrichment_type: Literal["REFERENTIEL", "WEB", "GENERATIF", "EN_ATTENTE"] = Field(
        description="Type of enrichment to perform"
    )

    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall confidence score for this routing decision"
    )

    justification: str = Field(
        description="Brief explanation of why this routing was chosen"
    )

    # Data packages for each enrichment type (only relevant one will be populated)
    amazon_data: Optional[List[AmazonProduct]] = Field(
        default=None,
        description="Amazon products found (for REFERENTIEL)"
    )

    web_sources: Optional[List[WebSource]] = Field(
        default=None,
        description="Web sources found (for WEB)"
    )

    generatif_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Data for generative enrichment (images, specs, docs)"
    )

    missing_data: Optional[List[str]] = Field(
        default=None,
        description="List of missing data (for EN_ATTENTE)"
    )

    # Search metadata
    search_summary: Dict[str, Any] = Field(
        description="Summary of search performed (languages, domains, results count)"
    )


class MatchingDetails(BaseModel):
    """Detailed matching information for scoring."""

    ean_match: bool = Field(default=False, description="EAN matched")
    ean_score: float = Field(default=0.0, description="EAN matching contribution")

    brand_match: bool = Field(default=False, description="Brand matched")
    brand_score: float = Field(default=0.0, description="Brand matching contribution")

    model_match: bool = Field(default=False, description="Model/reference matched")
    model_score: float = Field(default=0.0, description="Model matching contribution")

    category_match: bool = Field(default=False, description="Category matched")
    category_score: float = Field(default=0.0, description="Category matching contribution")

    overall_score: float = Field(ge=0.0, le=1.0, description="Overall matching score")

    justification: str = Field(description="Explanation of the matching score")


class EnrichedData(BaseModel):
    """Enriched product data (output from subgraphs)."""

    # Core enriched content (always in French)
    titre_enrichi: Optional[str] = Field(default=None, description="Enriched product title")
    description_enrichie: Optional[str] = Field(default=None, description="Enriched description")
    points_forts: Optional[List[str]] = Field(default=None, description="Key product features")
    caracteristiques: Optional[Dict[str, Any]] = Field(default=None, description="Product characteristics")
    specifications_techniques: Optional[Dict[str, Any]] = Field(default=None, description="Technical specifications")

    # Media
    images: Optional[List[str]] = Field(default=None, description="Product images URLs")
    images_quality: Optional[str] = Field(default=None, description="Image quality assessment")

    # Sources used
    sources_used: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Sources used for enrichment"
    )

    # Languages of sources
    languages_found: List[str] = Field(
        default_factory=list,
        description="Languages of sources found"
    )


class EnrichmentReport(BaseModel):
    """Complete enrichment report (note d'enrichissement)."""

    # General information
    article_reference: str = Field(description="Article reference")
    enrichment_type: str = Field(description="Type of enrichment applied")
    enrichment_status: str = Field(description="Status: COMPLETE, EN_ATTENTE, REJECTED")

    # Scores
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence score (0-100%)")
    matching_score: Optional[float] = Field(default=None, description="Rigorous matching score")
    matching_details: Optional[MatchingDetails] = Field(default=None, description="Detailed matching info")

    # Processing info
    processing_timestamp: str = Field(description="Processing timestamp")
    processing_time_seconds: float = Field(description="Processing duration in seconds")

    # Treatment summary
    treatment_summary: Dict[str, Any] = Field(
        description="Summary of treatment performed"
    )

    # Enriched data
    enriched_data: Optional[EnrichedData] = Field(
        default=None,
        description="The enriched product data"
    )

    # Warnings and recommendations
    warnings: List[str] = Field(default_factory=list, description="Warnings if applicable")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")

    # Metadata
    sources_used: List[Dict[str, Any]] = Field(default_factory=list, description="All sources used")
    languages_found: List[str] = Field(default_factory=list, description="Languages of sources")

    # For EN_ATTENTE status
    missing_data: Optional[List[str]] = Field(default=None, description="Missing data list")
    suggestions: Optional[List[str]] = Field(default=None, description="Suggestions to complete data")

    # For REJECTED status
    rejection_reason: Optional[str] = Field(default=None, description="Reason for rejection")


# =============================================================================
# GRAPH STATES
# =============================================================================

class EnrichmentState(MessagesState):
    """Main state for the Article Enrichment workflow."""

    # =========================================================================
    # INPUT DATA
    # =========================================================================

    article_payload: ArticlePayload = Field(
        description="Original article payload"
    )

    # =========================================================================
    # RESEARCH PHASE (deep_researcher)
    # =========================================================================

    research_brief: Optional[ResearchBrief] = Field(
        default=None,
        description="Structured research brief"
    )

    # Search results
    amazon_products_found: List[AmazonProduct] = Field(
        default_factory=list,
        description="Amazon products found during search"
    )

    web_sources_found: List[WebSource] = Field(
        default_factory=list,
        description="Web sources found during search"
    )

    technical_docs_found: List[TechnicalDocument] = Field(
        default_factory=list,
        description="Technical documents found"
    )

    # Search metadata
    search_languages_used: List[str] = Field(
        default_factory=list,
        description="Languages used for searches"
    )

    search_domains_targeted: List[str] = Field(
        default_factory=list,
        description="Domains targeted during search"
    )

    search_iterations_count: int = Field(
        default=0,
        description="Number of search iterations performed"
    )

    # =========================================================================
    # ROUTING DECISION
    # =========================================================================

    routing_decision: Optional[RoutingDecision] = Field(
        default=None,
        description="Routing decision made by deep_researcher"
    )

    enrichment_type: Optional[str] = Field(
        default=None,
        description="Type of enrichment selected"
    )

    # =========================================================================
    # SUBGRAPH OUTPUTS
    # =========================================================================

    # Matching and scoring
    matching_details: Optional[MatchingDetails] = Field(
        default=None,
        description="Detailed matching information from subgraph"
    )

    confidence_score_final: Optional[float] = Field(
        default=None,
        description="Final confidence score from subgraph"
    )

    # Enriched data
    enriched_data: Optional[EnrichedData] = Field(
        default=None,
        description="Enriched product data from subgraph"
    )

    # =========================================================================
    # FINAL REPORT
    # =========================================================================

    enrichment_report: Optional[EnrichmentReport] = Field(
        default=None,
        description="Complete enrichment report (note d'enrichissement)"
    )

    # Processing metadata
    processing_start_time: Optional[datetime.datetime] = Field(
        default=None,
        description="Processing start timestamp"
    )

    processing_end_time: Optional[datetime.datetime] = Field(
        default=None,
        description="Processing end timestamp"
    )

    # Status tracking
    enrichment_status: Optional[str] = Field(
        default=None,
        description="Current enrichment status"
    )

    warnings: List[str] = Field(
        default_factory=list,
        description="Warnings accumulated during processing"
    )

    # For EN_ATTENTE cases
    missing_data_list: List[str] = Field(
        default_factory=list,
        description="List of missing data items"
    )

    suggestions_list: List[str] = Field(
        default_factory=list,
        description="Suggestions to complete missing data"
    )

    # For REJECTED cases
    rejection_reason: Optional[str] = Field(
        default=None,
        description="Reason for rejection if applicable"
    )


class AmazonSubgraphState(MessagesState):
    """State for the REFERENTIEL (Amazon) subgraph."""

    # Input from routing
    amazon_products: List[AmazonProduct] = Field(
        description="Amazon products to process"
    )

    article_payload: ArticlePayload = Field(
        description="Original article payload for matching"
    )

    # Amazon API data (future implementation)
    amazon_api_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Complete data from Amazon API"
    )

    # Matching and scoring
    matching_details: MatchingDetails = Field(
        description="Matching details with rigorous scoring"
    )

    # Enriched content
    enriched_data: Optional[EnrichedData] = Field(
        default=None,
        description="Enriched data from Amazon"
    )

    # Rejection handling
    rejected: bool = Field(default=False, description="Whether this match was rejected")
    rejection_reason: Optional[str] = Field(default=None, description="Reason for rejection")


class WebSubgraphState(MessagesState):
    """State for the WEB enrichment subgraph."""

    # Input from routing
    web_sources: List[WebSource] = Field(
        description="Web sources to extract and aggregate"
    )

    article_payload: ArticlePayload = Field(
        description="Original article payload for matching"
    )

    # Extracted content
    extracted_contents: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Extracted and parsed content from sources"
    )

    # Aggregated data
    aggregated_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Aggregated data from all sources"
    )

    # Matching and scoring
    matching_details: MatchingDetails = Field(
        description="Matching details with consensus scoring"
    )

    # Enriched content
    enriched_data: Optional[EnrichedData] = Field(
        default=None,
        description="Enriched data synthesized from web sources"
    )

    # Rejection handling
    rejected: bool = Field(default=False, description="Whether sources were rejected")
    rejection_reason: Optional[str] = Field(default=None, description="Reason for rejection")


class GenerativeSubgraphState(MessagesState):
    """State for the GENERATIF enrichment subgraph."""

    # Input from routing
    article_payload: ArticlePayload = Field(
        description="Original article payload"
    )

    generatif_data: Dict[str, Any] = Field(
        description="Data for generative enrichment (images, specs, docs)"
    )

    # Product profile analysis
    product_profile: Optional[str] = Field(
        default=None,
        description="Product family profile determined"
    )

    # Technical specs extracted
    technical_specifications: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Technical specifications extracted from docs"
    )

    # Generated content
    enriched_data: Optional[EnrichedData] = Field(
        default=None,
        description="AI-generated enriched data"
    )

    # Quality scoring
    matching_details: Optional[MatchingDetails] = Field(
        default=None,
        description="Quality and completeness scoring"
    )

    # Rejection handling
    rejected: bool = Field(default=False, description="Whether generation was rejected")
    rejection_reason: Optional[str] = Field(default=None, description="Reason for rejection")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_initial_enrichment_state(article_payload: ArticlePayload) -> EnrichmentState:
    """
    Create initial enrichment state from article payload.

    Args:
        article_payload: The article payload to enrich

    Returns:
        Initialized EnrichmentState
    """
    return EnrichmentState(
        messages=[],
        article_payload=article_payload,
        processing_start_time=datetime.datetime.now(),
        enrichment_status="EN_COURS"
    )


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
    import re

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
    import re

    match = re.search(r'https?://(?:www\.)?([^/]+)', url)
    if match:
        return match.group(1)

    return None
