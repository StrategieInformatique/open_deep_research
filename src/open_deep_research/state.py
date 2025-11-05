"""Graph state definitions and data structures for the Deep Research agent."""

import operator
import re
from typing import Annotated, Optional, Dict, Any, List
from urllib.parse import urlparse

from langchain_core.messages import MessageLikeRepresentation
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


###################
# Structured Outputs for Article Enrichment
###################

class ArticlePayload(BaseModel):
    """Article payload from webhook - 100% compatible with Optimia_v2 ProductStateInput."""

    # ========== Identifiants ==========
    assistant_id: str = Field(default="product_description_crafter", description="Assistant identifier")
    ident: str = Field(description="Unique article identifier (ID in database)")
    ean: str = Field(default="", description="EAN barcode")

    # ========== Données produit principales ==========
    libelle: str = Field(default="", description="Product label/name")
    marque: str = Field(default="", description="Brand name")
    description: str = Field(default="", description="Existing product description")
    instructions: str = Field(default="", description="Product instructions")

    # ========== Données fournisseur ==========
    refFournisseur: Optional[str] = Field(default=None, description="Supplier reference")
    fournisseur: Optional[str] = Field(default=None, description="Supplier code")
    lib_fournisseur: Optional[str] = Field(default=None, description="Supplier name")

    # ========== Classification ==========
    famille: Optional[str] = Field(default=None, description="Product family code")
    lib_famille: Optional[str] = Field(default=None, description="Product family label")

    # ========== Attributs physiques ==========
    arcoul: str = Field(default="", description="Color code")
    coll: str = Field(default="", description="Collection")
    dimensions: str = Field(default="", description="Product dimensions")

    # ========== URLs et médias ==========
    url: str = Field(default="", description="Product page URL")
    images_url: Optional[str] = Field(default=None, description="Images URL or path")
    file_url: Optional[str] = Field(default=None, description="File URL")

    # ========== Propriétés personnalisées ==========
    nompropr: str = Field(default="", description="Custom property name")
    valpropr: str = Field(default="", description="Custom property value")

    # ========== Métadonnées ==========
    craft_try: int = Field(default=0, description="Number of craft attempts")
    prixttc: Optional[float] = Field(default=None, description="Price including tax")
    profilFamille: Optional[Dict[str, Any]] = Field(default=None, description="Family profile for future use")

    # ========== Champs additionnels pour enrichissement (compatibles) ==========
    images_urls: List[str] = Field(default_factory=list, description="List of image URLs (parsed from images_url)")
    fiche_technique_url: Optional[str] = Field(default=None, description="Technical sheet URL")
    documents_techniques: Optional[Dict[str, Any]] = Field(default=None, description="Technical documents")
    specifications_techniques: Optional[Dict[str, Any]] = Field(default=None, description="Technical specifications")

    @property
    def images_disponibles(self) -> bool:
        """Check if images are available from images_url or images_urls."""
        return bool(self.images_url or self.images_urls)

    @property
    def article_id(self) -> str:
        """Alias for ident (backward compatibility)."""
        return self.ident

    @property
    def reference_fournisseur(self) -> Optional[str]:
        """Alias for refFournisseur (backward compatibility)."""
        return self.refFournisseur

    @property
    def famille_produit(self) -> Optional[str]:
        """Alias for famille (backward compatibility)."""
        return self.famille

class AmazonProduct(BaseModel):
    """Amazon product found during enrichment."""

    asin: str = Field(description="Amazon Standard Identification Number (10 characters)")
    domain: str = Field(description="Amazon domain (e.g., amazon.fr, amazon.com)")
    url: str = Field(description="Full product URL")
    title: Optional[str] = Field(default=None, description="Product title")
    score: float = Field(default=0.0, description="Relevance score (0-1)")
    content_preview: Optional[str] = Field(default=None, description="Content preview from search")

class WebSource(BaseModel):
    """Web source found during enrichment."""

    url: str = Field(description="Source URL")
    domain: str = Field(description="Domain name")
    title: Optional[str] = Field(default=None, description="Page title")
    score: float = Field(default=0.0, description="Relevance score (0-1)")
    content_preview: Optional[str] = Field(default=None, description="Content preview")

class RoutingDecision(BaseModel):
    """Routing decision for article enrichment."""

    enrichment_type: str = Field(description="Type: REFERENTIEL, WEB, GENERATIF, EN_ATTENTE")
    confidence_score: float = Field(description="Confidence score (0-1)")
    justification: str = Field(description="Justification for the routing decision")
    next_subgraph: str = Field(description="Next subgraph to execute")
    amazon_products: List[AmazonProduct] = Field(default_factory=list, description="Amazon products found")
    web_sources: List[WebSource] = Field(default_factory=list, description="Web sources found")
    search_summary: Dict[str, Any] = Field(default_factory=dict, description="Search summary metadata")

class ConductResearch(BaseModel):
    """Call this tool to conduct research on a specific topic."""
    research_topic: str = Field(
        description="The topic to research. Should be a single topic, and should be described in high detail (at least a paragraph).",
    )

class ResearchComplete(BaseModel):
    """Call this tool to indicate that the research is complete."""

class Summary(BaseModel):
    """Research summary with key findings."""

    summary: str
    key_excerpts: str

class ClarifyWithUser(BaseModel):
    """Model for user clarification requests."""

    need_clarification: bool = Field(
        description="Whether the user needs to be asked a clarifying question.",
    )
    question: str = Field(
        description="A question to ask the user to clarify the report scope",
    )
    verification: str = Field(
        description="Verify message that we will start research after the user has provided the necessary information.",
    )

class ResearchQuestion(BaseModel):
    """Research question and brief for guiding research."""

    research_brief: str = Field(
        description="A research question that will be used to guide the research.",
    )


###################
# State Definitions
###################

def override_reducer(current_value, new_value):
    """Reducer function that allows overriding values in state."""
    if isinstance(new_value, dict) and new_value.get("type") == "override":
        return new_value.get("value", new_value)
    else:
        return operator.add(current_value, new_value)
    
class AgentInputState(MessagesState):
    """InputState is only 'messages'."""

class AgentState(MessagesState):
    """Main agent state containing messages and research data."""

    supervisor_messages: Annotated[list[MessageLikeRepresentation], override_reducer]
    research_brief: Optional[str]
    raw_notes: Annotated[list[str], override_reducer] = []
    notes: Annotated[list[str], override_reducer] = []
    final_report: str

    # Article enrichment fields
    article_payload: Optional[ArticlePayload] = None
    amazon_products: Annotated[List[AmazonProduct], override_reducer] = []
    web_sources: Annotated[List[WebSource], override_reducer] = []
    routing_decision: Optional[RoutingDecision] = None

class SupervisorState(TypedDict):
    """State for the supervisor that manages research tasks."""

    supervisor_messages: Annotated[list[MessageLikeRepresentation], override_reducer]
    research_brief: str
    notes: Annotated[list[str], override_reducer] = []
    research_iterations: int = 0
    raw_notes: Annotated[list[str], override_reducer] = []

    # Article enrichment fields for supervisor
    article_payload: Optional[ArticlePayload]
    amazon_products: Annotated[List[AmazonProduct], override_reducer]
    web_sources: Annotated[List[WebSource], override_reducer]

class ResearcherState(TypedDict):
    """State for individual researchers conducting research."""

    researcher_messages: Annotated[list[MessageLikeRepresentation], operator.add]
    tool_call_iterations: int = 0
    research_topic: str
    compressed_research: str
    raw_notes: Annotated[list[str], override_reducer] = []

    # Article enrichment fields for researcher
    search_phase: Optional[str]  # "amazon" or "web"
    article_payload: Optional[ArticlePayload]

class ResearcherOutputState(BaseModel):
    """Output state from individual researchers."""

    compressed_research: str
    raw_notes: Annotated[list[str], override_reducer] = []

    # Article enrichment outputs
    amazon_products: Annotated[List[AmazonProduct], override_reducer] = []
    web_sources: Annotated[List[WebSource], override_reducer] = []
###################
# Helper Functions for Article Enrichment
###################

def extract_asin_from_url(url: str) -> Optional[str]:
    """
    Extract ASIN (10-character code) from Amazon URL.

    Args:
        url: Amazon product URL

    Returns:
        ASIN if found, None otherwise

    Examples:
        - https://www.amazon.fr/dp/B0XXXXXXXX → B0XXXXXXXX
        - https://www.amazon.it/product/B0YYYYYYYY → B0YYYYYYYY
    """
    if not url or "amazon" not in url.lower():
        return None

    # Pattern 1: /dp/{ASIN}
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    if match:
        return match.group(1)

    # Pattern 2: /product/{ASIN}
    match = re.search(r'/product/([A-Z0-9]{10})', url)
    if match:
        return match.group(1)

    # Pattern 3: /gp/product/{ASIN}
    match = re.search(r'/gp/product/([A-Z0-9]{10})', url)
    if match:
        return match.group(1)

    return None


def extract_domain_from_url(url: str) -> Optional[str]:
    """
    Extract domain from URL.

    Args:
        url: Full URL

    Returns:
        Domain name (e.g., 'amazon.fr')

    Examples:
        - https://www.amazon.fr/dp/B123 → amazon.fr
        - https://example.com/page → example.com
    """
    if not url:
        return None

    try:
        parsed = urlparse(url)
        domain = parsed.netloc

        # Remove 'www.' prefix
        if domain.startswith('www.'):
            domain = domain[4:]

        return domain
    except Exception:
        return None
