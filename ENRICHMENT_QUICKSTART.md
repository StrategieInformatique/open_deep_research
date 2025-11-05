# 🚀 Quick Start - Article Enrichment System

Ce guide vous permet de tester rapidement le système d'enrichissement d'articles.

## ✅ Prérequis

1. **Clés API requises** :
   ```bash
   export TAVILY_API_KEY="tvly-YOUR_KEY_HERE"
   export OPENAI_API_KEY="sk-YOUR_KEY_HERE"
   ```

2. **Dépendances Python** :
   ```bash
   pip install tavily-python langchain langchain-openai langgraph
   ```

## 📁 Fichiers Créés

### Fichiers Core
- ✅ `src/open_deep_research/prompts_enrichment.py` - Prompts système
- ✅ `src/open_deep_research/configuration_enrichment.py` - Configuration
- ✅ `src/open_deep_research/state_enrichment.py` - États et structures
- ✅ `src/open_deep_research/utils_enrichment.py` - Outils Tavily
- ✅ `src/open_deep_research/article_enrichment_graph.py` - Graph principal

### Fichiers de Test
- ✅ `examples/test_enrichment.py` - Script de test avec exemples

## 🧪 Test Rapide

### 1. Tester avec un Article Amazon

```bash
cd /Users/devopsstudio/Repoz/pro/open_deep_research
python examples/test_enrichment.py
```

Ce script teste par défaut un **MacBook Pro** qui devrait être trouvé sur Amazon.

**Output attendu** :
```
🔍 PHASE 1: Searching Amazon across multiple countries...
✅ Amazon search completed. Results:...
✅ Found 1 Amazon product(s)!
✅ Confidence score 0.50 >= threshold. Routing to REFERENTIEL.

📊 ENRICHMENT RESULTS
==========================================
📦 Article: Apple MacBook Pro 14 pouces
   EAN: 0194252721124

🎯 ROUTING DECISION: REFERENTIEL
   Confidence Score: 0.50
   Justification: Product found on Amazon with 1 match(es)...

🛒 Amazon Products Found: 1
   1. ASIN: B08X123456
      Domain: amazon.fr
      URL: https://www.amazon.fr/dp/B08X123456
      Title: Apple MacBook Pro...

➡️  Next Node: REFERENTIEL_subgraph
```

### 2. Tester d'Autres Scénarios

Éditez `examples/test_enrichment.py` et décommentez les tests :

```python
# Test 2: Product likely on web (not Amazon)
await test_enrichment(ARTICLE_WEB_EXAMPLE)

# Test 3: Product for generative enrichment
await test_enrichment(ARTICLE_GENERATIF_EXAMPLE)

# Test 4: Product with missing data
await test_enrichment(ARTICLE_PENDING_EXAMPLE)
```

## 📊 Comprendre les Résultats

### Le Node `deep_researcher` Effectue :

#### **Phase 1 : Recherche Amazon** 🛒
- Recherche sur 6 domaines : `.fr, .it, .com, .es, .de, .uk`
- Requêtes multilingues (FR, EN, IT, ES, DE)
- Extraction automatique des ASIN
- Si trouvé → Route vers **REFERENTIEL**

#### **Phase 2 : Recherche Web** 🌐
- Ne se déclenche QUE si Phase 1 échoue
- Recherche générale sur le web
- Identifie sites fabricants, retailers, bases de specs
- Si 2+ sources trouvées → Route vers **WEB**

#### **Phase 3 : Vérification GENERATIF** ✨
- Ne se déclenche QUE si Phase 1 et 2 échouent
- Vérifie disponibilité images + données techniques
- Si disponible → Route vers **GENERATIF**
- Sinon → Route vers **EN_ATTENTE**

### Output : Décision de Routing

Le `deep_researcher` retourne :
```python
RoutingDecision(
    enrichment_type="REFERENTIEL" | "WEB" | "GENERATIF" | "EN_ATTENTE",
    confidence_score=0.0-1.0,
    justification="Explication de la décision",
    amazon_data=[...],        # Si REFERENTIEL
    web_sources=[...],        # Si WEB
    generatif_data={...},     # Si GENERATIF
    missing_data=[...],       # Si EN_ATTENTE
    search_summary={...}
)
```

## 🎯 Types de Routing

### 1️⃣ REFERENTIEL (Amazon)
**Conditions** :
- ✅ ASIN trouvé sur Amazon
- ✅ Confidence score ≥ 0.75

**Données retournées** :
```python
amazon_data=[
    AmazonProduct(
        asin="B08X123456",
        domain="amazon.fr",
        url="https://www.amazon.fr/dp/B08X123456",
        title="Product Title",
        ...
    )
]
```

### 2️⃣ WEB (Multi-sources)
**Conditions** :
- ❌ PAS trouvé sur Amazon
- ✅ 2+ sources web avec score ≥ 0.5
- ✅ Confidence score ≥ 0.60

**Données retournées** :
```python
web_sources=[
    WebSource(
        url="https://manufacturer.com/product",
        domain="manufacturer.com",
        relevance_score=0.85,
        title="Product Page",
        ...
    ),
    WebSource(...),
]
```

### 3️⃣ GENERATIF (IA Native)
**Conditions** :
- ❌ PAS trouvé sur Amazon
- ❌ PAS trouvé sur web
- ✅ Images disponibles
- ✅ Données techniques disponibles

**Données retournées** :
```python
generatif_data={
    "images": ["url1.jpg", "url2.jpg"],
    "technical_specs": {...},
    "technical_docs": ["doc1.pdf"],
    "datasheet_url": "datasheet.pdf"
}
```

### 4️⃣ EN_ATTENTE (Pending)
**Conditions** :
- ❌ PAS trouvé sur Amazon
- ❌ PAS trouvé sur web
- ❌ Données manquantes pour GENERATIF

**Données retournées** :
```python
missing_data=[
    "Images produit",
    "Données techniques ou fiche technique"
]
```

## 🔧 Configuration

### Modifier les Budgets de Recherche

Éditez `src/open_deep_research/configuration_enrichment.py` :

```python
class EnrichmentConfiguration(BaseModel):
    # Budgets de recherche
    max_amazon_searches: int = 3      # Max recherches Amazon
    max_web_searches: int = 3          # Max recherches web
    max_technical_searches: int = 2    # Max recherches techniques

    # Seuils de scoring
    referentiel_min: float = 0.75      # Seuil REFERENTIEL
    web_min: float = 0.60              # Seuil WEB
    generatif_min: float = 0.50        # Seuil GENERATIF

    # Tavily settings
    tavily_search_depth: str = "advanced"  # "basic" ou "advanced"
    tavily_max_results: int = 10            # Résultats par recherche
```

### Modifier les Domaines Amazon

```python
class AmazonDomains(BaseModel):
    domains: List[str] = [
        "amazon.fr",
        "amazon.it",
        "amazon.com",
        "amazon.es",
        "amazon.de",
        "amazon.co.uk"
    ]
```

### Modifier les Langues de Recherche

```python
class SearchLanguages(BaseModel):
    languages: List[str] = [
        "french",
        "english",
        "italian",
        "spanish",
        "german"
    ]
```

## 📝 Créer Votre Propre Test

```python
from open_deep_research.article_enrichment_graph import enrichment_graph
from open_deep_research.state_enrichment import ArticlePayload, create_initial_enrichment_state

# Créer votre article
article = ArticlePayload(
    article_id="CUSTOM001",
    libelle="Votre Produit",
    marque="Votre Marque",
    ean="1234567890123",  # Optionnel
    reference_fournisseur="REF-001",  # Optionnel
    famille_produit="Catégorie",
    images_disponibles=False,
)

# Créer l'état initial
state = create_initial_enrichment_state(article)

# Exécuter le graph
final_state = await enrichment_graph.ainvoke(
    state,
    config={
        "configurable": {
            "model": "openai:gpt-4o-mini",
        }
    }
)

# Analyser les résultats
routing = final_state["routing_decision"]
print(f"Type: {routing.enrichment_type}")
print(f"Confidence: {routing.confidence_score}")
```

## 🐛 Dépannage

### Erreur : `TAVILY_API_KEY not set`
```bash
export TAVILY_API_KEY="tvly-YOUR_KEY"
```
Obtenez une clé sur [tavily.com](https://tavily.com)

### Erreur : `OPENAI_API_KEY not set`
```bash
export OPENAI_API_KEY="sk-YOUR_KEY"
```

### Import Error
```bash
pip install tavily-python langchain langchain-openai langgraph
```

### Coûts Tavily
- **Basic search** : 1 crédit/requête
- **Advanced search** : 2 crédits/requête (recommandé)
- **Budget par article** : ~6-16 crédits selon phases

**Compte gratuit Tavily** : 1000 crédits/mois

## ✅ Prochaines Étapes

### Phase Actuelle ✅
- ✅ Node `deep_researcher` implémenté
- ✅ Recherche Amazon multilingue
- ✅ Recherche web générale
- ✅ Décision de routing automatique
- ✅ Output des résultats de recherche

### Prochaine Phase ⏭️
Après validation du `deep_researcher`, implémenter les **subgraphs** :

1. **`amazon_subgraph`** (REFERENTIEL)
   - Appel API Amazon (ou parsing avancé)
   - Scoring rigoureux de correspondance
   - Réécriture du contenu en français
   - Enrichissement des données produit

2. **`web_subgraph`** (WEB)
   - Extraction du contenu des sources
   - Agrégation et déduplication
   - Scoring de consensus entre sources
   - Synthèse intelligente en français

3. **`generative_subgraph`** (GENERATIF)
   - Analyse du profil produit
   - Parsing des fiches techniques
   - Génération du contenu par IA
   - Validation de cohérence

4. **`report_generator`**
   - Génération de la Note d'Enrichissement
   - Scores de confiance détaillés
   - Recommandations et avertissements

## 📖 Documentation Complète

- **`ENRICHMENT_SETUP.md`** : Architecture et design détaillés
- **`prompts_enrichment.py`** : Tous les prompts avec explications
- **`configuration_enrichment.py`** : Configuration complète avec commentaires
- **`state_enrichment.py`** : Structures de données documentées

## 💡 Support

Pour toute question sur l'implémentation :
1. Consultez les prompts dans `prompts_enrichment.py`
2. Vérifiez la configuration dans `configuration_enrichment.py`
3. Examinez les états dans `state_enrichment.py`
4. Testez avec `examples/test_enrichment.py`

---

**🚀 Vous êtes prêt à tester le système d'enrichissement !**

Exécutez simplement :
```bash
python examples/test_enrichment.py
```
