# 📋 Configuration du Système d'Enrichissement d'Articles

## ✅ Fichiers Créés

Trois fichiers fondamentaux ont été créés pour démarrer votre projet d'enrichissement :

### 1️⃣ `src/open_deep_research/prompts_enrichment.py`
**Rôle** : Contient tous les prompts système pour l'enrichissement d'articles

**Contenu** :
- ✅ **`article_to_research_brief_prompt`** : Transforme le payload article en brief de recherche structuré
- ✅ **`deep_researcher_article_enrichment_prompt`** : Prompt principal pour le `deep_researcher` qui effectue :
  - Recherche sur Amazon multi-pays (Phase 1)
  - Recherche web générale si Amazon échoue (Phase 2)
  - Recherche de documentation technique (Phase 3)
  - Décision de routage vers le bon subgraph (Phase 4)
- ✅ **`routing_decision_instructions`** : Instructions pour structurer la décision de routage
- ✅ **Guides de support** :
  - `amazon_asin_extraction_guide` : Comment extraire les ASIN des URLs
  - `multi_language_query_guide` : Formuler des requêtes multilingues
  - `tavily_search_optimization_guide` : Optimiser l'utilisation de Tavily

**Points clés** :
- Prompts inspirés des prompts originaux (bien structurés, détaillés)
- Utilisation optimale de Tavily selon la documentation officielle
- Recherches multilingues (FR, EN, IT, ES, DE) pour maximiser les chances de trouver les produits
- Budgets stricts pour éviter les recherches excessives
- Instructions pour extraction d'ASIN et détection Amazon

---

### 2️⃣ `src/open_deep_research/configuration_enrichment.py`
**Rôle** : Configuration complète du système d'enrichissement

**Classes principales** :

#### `EnrichmentType` (Enum)
```python
REFERENTIEL = "REFERENTIEL"  # Amazon
WEB = "WEB"                  # Multi-sources web
GENERATIF = "GENERATIF"      # IA native
EN_ATTENTE = "EN_ATTENTE"    # Données manquantes
```

#### `EnrichmentConfiguration`
Configuration complète incluant :

**Recherche** :
- `max_search_iterations = 8` : Maximum de recherches totales
- `max_amazon_searches = 3` : Maximum pour phase Amazon
- `max_web_searches = 3` : Maximum pour phase web
- `max_technical_searches = 2` : Maximum pour phase technique
- `tavily_search_depth = "advanced"` : Profondeur de recherche (2 crédits)
- `tavily_max_results = 10` : Résultats par recherche

**Domaines Amazon** :
```python
["amazon.fr", "amazon.it", "amazon.com", "amazon.es", "amazon.de", "amazon.co.uk"]
```

**Langues de recherche** :
```python
["french", "english", "italian", "spanish", "german"]
```

**Seuils de scoring** :
- `referentiel_min = 0.75` : Score minimum pour router vers REFERENTIEL
- `web_min = 0.60` : Score minimum pour router vers WEB
- `generatif_min = 0.50` : Score minimum pour GENERATIF
- Poids de matching :
  - EAN match = 0.40
  - Brand match = 0.25
  - Model match = 0.25
  - Category match = 0.10

**Modèles** :
- `deep_researcher_model = "openai:gpt-4o"` : Modèle principal
- `brief_generation_model = "openai:gpt-4o-mini"` : Brief (plus léger)
- `report_generation_model = "openai:gpt-4o"` : Rapport final
- Modèles spécialisés pour chaque subgraph

**Fonctions helper** :
- `calculate_matching_score()` : Calculer score de correspondance
- `should_route_to_referentiel()` : Décision de routage
- `should_route_to_web()` : Décision de routage
- `get_default_enrichment_config()` : Config par défaut

---

### 3️⃣ `src/open_deep_research/state_enrichment.py`
**Rôle** : Définitions des états et structures de données

**Structured Outputs** (pour `.with_structured_output()`) :

#### 📦 **`ArticlePayload`**
Payload d'entrée avec les informations article :
```python
article_id: str
libelle: str
marque: str
ean: Optional[str]
reference_fournisseur: Optional[str]
famille_produit: Optional[str]
images_disponibles: bool
images_urls: Optional[List[str]]
fiche_technique_url: Optional[str]
```

#### 📝 **`ResearchBrief`**
Brief de recherche structuré :
```python
product_identity: Dict[str, Any]
search_queries: Dict[str, List[str]]  # Par langue
search_strategy: Dict[str, Any]
success_criteria: Dict[str, Any]
```

#### 🛒 **`AmazonProduct`**
Produit Amazon trouvé :
```python
asin: str  # 10 caractères
domain: str  # amazon.fr, amazon.com, etc.
url: str
title: Optional[str]
price: Optional[str]
rating: Optional[float]
metadata: Optional[Dict[str, Any]]
```

#### 🌐 **`WebSource`**
Source web trouvée :
```python
url: str
title: Optional[str]
domain: str
relevance_score: float  # Score Tavily (0.0-1.0)
language: Optional[str]
source_type: Optional[str]  # manufacturer, retailer, etc.
```

#### 📄 **`TechnicalDocument`**
Document technique trouvé :
```python
url: str
document_type: str  # PDF, webpage
content_extracted: Optional[str]
specifications_found: Optional[Dict[str, Any]]
```

#### 🎯 **`RoutingDecision`**
Décision de routage du `deep_researcher` :
```python
enrichment_type: Literal["REFERENTIEL", "WEB", "GENERATIF", "EN_ATTENTE"]
confidence_score: float
justification: str
amazon_data: Optional[List[AmazonProduct]]
web_sources: Optional[List[WebSource]]
generatif_data: Optional[Dict[str, Any]]
missing_data: Optional[List[str]]
search_summary: Dict[str, Any]
```

#### 📊 **`MatchingDetails`**
Détails du scoring de correspondance :
```python
ean_match: bool
brand_match: bool
model_match: bool
category_match: bool
overall_score: float
justification: str
```

#### 💎 **`EnrichedData`**
Données enrichies (output) :
```python
titre_enrichi: Optional[str]
description_enrichie: Optional[str]
points_forts: Optional[List[str]]
caracteristiques: Optional[Dict[str, Any]]
specifications_techniques: Optional[Dict[str, Any]]
images: Optional[List[str]]
sources_used: List[Dict[str, Any]]
languages_found: List[str]
```

#### 📑 **`EnrichmentReport`**
Note d'enrichissement complète :
```python
article_reference: str
enrichment_type: str
enrichment_status: str
confidence_score: float
matching_score: Optional[float]
processing_timestamp: str
processing_time_seconds: float
treatment_summary: Dict[str, Any]
enriched_data: Optional[EnrichedData]
warnings: List[str]
recommendations: List[str]
```

**Graph States** :

#### 🔄 **`EnrichmentState`**
État principal du workflow (hérite de `MessagesState`) :
- Input : `article_payload`
- Research : `research_brief`, résultats de recherche
- Routing : `routing_decision`, `enrichment_type`
- Output : `enriched_data`, `enrichment_report`
- Metadata : timestamps, status, warnings

#### 🛒 **`AmazonSubgraphState`**
État pour le subgraph REFERENTIEL (Amazon)

#### 🌐 **`WebSubgraphState`**
État pour le subgraph WEB

#### ✨ **`GenerativeSubgraphState`**
État pour le subgraph GENERATIF

**Fonctions helper** :
- `create_initial_enrichment_state()` : Créer état initial
- `extract_asin_from_url()` : Extraire ASIN d'une URL Amazon
- `extract_domain_from_url()` : Extraire domaine d'une URL

---

## 🎯 Ce Qui a Été Accompli

### ✅ Prompts Adaptés
1. **Transformation payload → brief** : Inspiré de `transform_messages_into_research_topic_prompt`
2. **Deep researcher multilingue** : Inspiré de `lead_researcher_prompt` + `research_system_prompt`
3. **Guides de support** : ASIN extraction, multi-language queries, Tavily optimization

### ✅ Configuration Complète
1. **Budgets de recherche** : Limites claires pour éviter les coûts excessifs
2. **Domaines Amazon** : Multi-pays (.fr, .it, .com, .es, .de, .uk)
3. **Langues de recherche** : FR, EN, IT, ES, DE
4. **Seuils de scoring** : Critères de décision pour chaque type d'enrichissement
5. **Modèles** : Configuration flexible (GPT-4o, GPT-4o-mini, etc.)

### ✅ États Structurés
1. **Structured Outputs** : 10+ classes Pydantic pour `.with_structured_output()`
2. **Graph States** : États pour le workflow principal + 3 subgraphs
3. **Helper Functions** : Extraction ASIN, création d'état initial

---

## 🔍 Comment Ça Répond à Votre Besoin Initial

### Votre Besoin #1 : Détecter disponibilité Amazon + ASIN
✅ **Résolu par** :
- `deep_researcher_article_enrichment_prompt` : Phase 1 dédiée à la recherche Amazon
- Utilisation de `include_domains` Tavily pour cibler tous les Amazon
- `AmazonProduct` structured output avec `asin` + `domain`
- `extract_asin_from_url()` helper function
- Requêtes multilingues pour trouver produits sur Amazon international

**Exemple de workflow** :
```python
# deep_researcher effectue :
tavily_search(
    queries=[
        f"{ean} amazon",
        f"{brand} {model} amazon",
        f"{brand} {model} product"
    ],
    include_domains=["amazon.fr", "amazon.it", "amazon.com", ...],
    search_depth="advanced",
    max_results=10
)

# Output :
routing_decision = RoutingDecision(
    enrichment_type="REFERENTIEL",
    amazon_data=[
        AmazonProduct(
            asin="B08X123456",
            domain="amazon.fr",
            url="https://www.amazon.fr/dp/B08X123456",
            ...
        )
    ]
)
```

### Votre Besoin #2 : Recherche Web si pas sur Amazon
✅ **Résolu par** :
- `deep_researcher_article_enrichment_prompt` : Phase 2 dédiée à la recherche web
- Ne se déclenche QUE si Phase 1 (Amazon) échoue
- Recherche multi-sources avec Tavily (sans restriction de domaines)
- `WebSource` structured output avec scores de pertinence
- Requêtes multilingues pour sites fabricants internationaux

**Exemple de workflow** :
```python
# Si Amazon échoue, deep_researcher effectue :
tavily_search(
    queries=[
        f"{brand} {model} specifications",
        f"{marque} {modèle} fiche technique",
        f"{ean} technical datasheet"
    ],
    search_depth="advanced",
    max_results=10
    # Pas de include_domains = recherche large
)

# Output :
routing_decision = RoutingDecision(
    enrichment_type="WEB",
    web_sources=[
        WebSource(
            url="https://manufacturer.com/product",
            relevance_score=0.85,
            domain="manufacturer.com",
            language="english",
            source_type="manufacturer"
        ),
        WebSource(
            url="https://retailer.it/prodotto",
            relevance_score=0.72,
            domain="retailer.it",
            language="italian",
            source_type="retailer"
        )
    ]
)
```

---

## 📊 Utilisation de Tavily - Best Practices Intégrées

### ✅ Recherches Multilingues
```python
# Requêtes formulées en plusieurs langues dans les prompts
queries = [
    f"{ean} amazon",                              # Universel
    f"{brand} {model} amazon",                    # Anglais
    f"{marque} {modèle} amazon",                  # Français
    f"{marca} {modelo} amazon",                   # Espagnol
    f"{marca} {modello} amazon"                   # Italien
]
```

### ✅ Filtrage par Domaines Amazon
```python
include_domains = [
    "amazon.fr", "amazon.it", "amazon.com",
    "amazon.es", "amazon.de", "amazon.co.uk"
]
```

### ✅ Search Depth Optimal
```python
search_depth = "advanced"  # 2 crédits mais meilleure précision
max_results = 10           # Large pour multi-pays
```

### ✅ Scoring des Résultats
```python
# Tavily retourne un score de pertinence (0.0-1.0)
# On filtre les sources avec score > 0.5
if source.relevance_score > 0.5:
    relevant_sources.append(source)
```

### ✅ Extraction de Contenu
```python
# Two-step process (recommandé par Tavily)
# Step 1: Search pour trouver URLs
# Step 2: Extract pour contenu complet
tavily_extract(
    urls=relevant_urls,
    extract_depth="advanced",
    format="markdown"
)
```

---

## 🚀 Prochaines Étapes Suggérées

### Étape 1 : Créer le Deep Researcher Node ⏭️
Implémenter le node `deep_researcher` qui :
1. Reçoit le `ArticlePayload`
2. Génère le `ResearchBrief`
3. Effectue les recherches (Amazon → Web → Technical)
4. Retourne la `RoutingDecision`

### Étape 2 : Créer les Subgraphs
Implémenter les 3 subgraphs :
- `amazon_subgraph` (REFERENTIEL)
- `web_subgraph` (WEB)
- `generative_subgraph` (GENERATIF)

### Étape 3 : Créer le Report Generator
Node final qui génère la `EnrichmentReport`

### Étape 4 : Assembler le Graph Principal
```python
START → deep_researcher → [routing] → subgraphs → report_generator → END
```

---

## 💡 Points d'Attention

### 🔴 Coûts Tavily
- **Basic search** : 1 crédit/requête
- **Advanced search** : 2 crédits/requête
- **Extract** : 1 crédit/5 extractions (basic), 2 crédits/5 (advanced)

**Budget estimé par article** :
- Phase Amazon : 2-3 recherches × 2 crédits = 4-6 crédits
- Phase Web (si nécessaire) : 2-3 recherches × 2 crédits = 4-6 crédits
- Phase Technical (si nécessaire) : 1-2 recherches × 2 crédits = 2-4 crédits
- **Total max** : ~16 crédits par article

### 🟢 Optimisations Possibles
1. Utiliser `basic` search pour follow-up queries
2. Implémenter du caching pour produits déjà recherchés
3. Batch processing pour réduire les appels API

### 🔵 Qualité des Prompts
Les prompts créés suivent les mêmes patterns que les prompts originaux :
- ✅ Instructions claires et structurées
- ✅ Budgets et limites explicites
- ✅ Exemples et guidelines
- ✅ Show Your Thinking (think_tool usage)
- ✅ Hard Limits pour éviter dépassements

---

## 📖 Documentation Référence

### Fichiers Originaux du Repo
- `src/open_deep_research/prompts.py` : Prompts de référence
- `src/open_deep_research/configuration.py` : Configuration de référence
- `src/open_deep_research/state.py` : États de référence
- `src/open_deep_research/deep_researcher.py` : Implémentation de référence

### Documentation Tavily
Documentation complète fournie et intégrée dans les prompts.

---

## ✅ Résumé

Vous disposez maintenant de :
1. ✅ **Prompts professionnels** inspirés des meilleurs prompts du repo
2. ✅ **Configuration complète** avec budgets, seuils, domaines
3. ✅ **États structurés** pour tout le workflow
4. ✅ **Support multilingue** (FR, EN, IT, ES, DE)
5. ✅ **Détection Amazon** avec extraction d'ASIN
6. ✅ **Recherche web** en fallback
7. ✅ **Best practices Tavily** intégrées

**Prêt pour l'implémentation du deep_researcher node !** 🚀

---

**Voulez-vous que je vous aide à implémenter le node `deep_researcher` en utilisant ces prompts et configurations ?**
