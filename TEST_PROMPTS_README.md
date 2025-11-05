# 🧪 Test Simple des Prompts d'Enrichissement

## Ce Qui a Été Créé (Les 3 Fichiers de Base)

### 1. `src/open_deep_research/prompts_enrichment.py`
Tous les prompts pour l'enrichissement d'articles :
- Transformation payload → brief de recherche
- Deep researcher avec recherches multilingues
- Guides d'optimisation Tavily

### 2. `src/open_deep_research/configuration_enrichment.py`
Configuration complète :
- Domaines Amazon (6 pays)
- Langues de recherche (5 langues)
- Budgets et seuils
- Poids de matching

### 3. `src/open_deep_research/state_enrichment.py`
Structures de données :
- 10 Structured Outputs (ArticlePayload, AmazonProduct, WebSource, etc.)
- 4 Graph States
- Helper functions (extraction ASIN, etc.)

---

## Script de Test Simple

### `test_prompts_simple.py`

Un script Python **simple** qui teste la logique **SANS LangGraph** :
- Charge un article
- Génère des requêtes multilingues
- Recherche sur Amazon (Phase 1)
- Recherche sur le web (Phase 2)
- Vérifie GENERATIF (Phase 3)
- Affiche la décision de routing

---

## 🚀 Comment Tester

### 1. Définir les Variables d'Environnement

```bash
export TAVILY_API_KEY="tvly-votre-clé"
export OPENAI_API_KEY="sk-votre-clé"  # Optionnel pour ce test
```

### 2. Lancer le Script

```bash
cd /Users/devopsstudio/Repoz/pro/open_deep_research
python test_prompts_simple.py
```

---

## 📊 Output Attendu

```
================================================================================
🧪 TEST DES PROMPTS D'ENRICHISSEMENT
================================================================================

📦 Article: BRAUN CENTRALE VAPEUR IS2144BK NOIR BRAUN
   EAN: 8021098280152
   Réf: IS2144BK

================================================================================
📝 GÉNÉRATION DES REQUÊTES MULTILINGUES
================================================================================

UNIVERSAL:
  - 8021098280152 amazon
  - 8021098280152 product

FRENCH:
  - BRAUN IS2144BK fiche technique
  - BRAUN IS2144BK amazon

ENGLISH:
  - BRAUN IS2144BK specifications
  - BRAUN IS2144BK amazon

ITALIAN:
  - BRAUN IS2144BK scheda tecnica

================================================================================
🛒 PHASE 1 : RECHERCHE AMAZON
================================================================================

🔍 Recherche Amazon avec 3 requête(s)...
  1. Requête: 8021098280152 amazon
     ✅ 2 résultat(s) trouvé(s)
  2. Requête: BRAUN IS2144BK specifications
     ✅ 1 résultat(s) trouvé(s)
  3. Requête: BRAUN IS2144BK fiche technique
     ✅ 0 résultat(s) trouvé(s)

📊 RÉSULTATS AMAZON : 3 produit(s)

  1. Braun IS2144BK Centrale Vapeur Noir
     ASIN: B0XXXXXXXX
     Domain: amazon.fr
     URL: https://www.amazon.fr/dp/B0XXXXXXXX
     Score: 0.89

  2. Braun CareStyle Compact IS 2144
     ASIN: B0YYYYYYYY
     Domain: amazon.it
     URL: https://www.amazon.it/dp/B0YYYYYYYY
     Score: 0.76

  3. Braun Steam Iron IS2144
     ASIN: B0ZZZZZZZZ
     Domain: amazon.com
     URL: https://www.amazon.com/dp/B0ZZZZZZZZ
     Score: 0.65

✅ DÉCISION : REFERENTIEL (Amazon trouvé)
   → 3 produit(s) Amazon trouvé(s)
   → Prochain step : amazon_subgraph

================================================================================
✅ TEST TERMINÉ
================================================================================
  Type d'enrichissement: REFERENTIEL
  Durée: 5.23s
================================================================================
```

---

## 🎯 Ce Que le Script Teste

### Phase 1 : Amazon
- ✅ Génération de requêtes multilingues
- ✅ Recherche sur 6 domaines Amazon
- ✅ Extraction automatique des ASIN
- ✅ Scoring de pertinence
- ✅ Décision : REFERENTIEL si trouvé

### Phase 2 : Web (si Amazon échoue)
- ✅ Recherche web générale
- ✅ Filtrage par score (> 0.5)
- ✅ Identification des domaines
- ✅ Décision : WEB si 2+ sources

### Phase 3 : Générativ (si Web échoue)
- ✅ Vérification images disponibles
- ✅ Vérification données techniques
- ✅ Décision : GENERATIF si données OK
- ✅ Sinon : EN_ATTENTE

---

## 🔧 Modifier l'Article de Test

Éditez `test_prompts_simple.py` ligne 17 :

```python
ARTICLE_TEST = {
    "article_id": "VOTRE-ID",
    "libelle": "VOTRE PRODUIT",
    "marque": "VOTRE MARQUE",
    "ean": "1234567890123",
    "reference_fournisseur": "REF-001",
    "famille_produit": "CATEGORIE",
    "images_disponibles": True,
    "images_urls": ["https://example.com/image.jpg"],
    "specifications_techniques": {
        "couleur": "Noir",
        "prix_ttc": 99.99
    }
}
```

---

## 📁 Fichiers Créés (Résumé)

```
src/open_deep_research/
├── prompts_enrichment.py          # Prompts système
├── configuration_enrichment.py    # Configuration
├── state_enrichment.py            # Structures de données
├── utils_enrichment.py            # Outils Tavily
└── utils/
    ├── logger_config.py           # Configuration logging
    └── log_helpers.py             # Helpers de logging

test_prompts_simple.py             # Script de test SIMPLE
```

---

## ✅ Avantages de Cette Approche

1. **Simple** : Pas de LangGraph, juste Python
2. **Rapide** : Test direct des prompts
3. **Clair** : Output structuré et lisible
4. **Indépendant** : Ne touche pas au repo original
5. **Testable** : Facile à modifier et réexécuter

---

## ⚠️ Ce Qui N'est PAS Implémenté (Volontairement)

- ❌ Graph LangGraph complet
- ❌ Subgraphs (amazon_subgraph, web_subgraph, etc.)
- ❌ Report generator
- ❌ Intégration avec le système original

**Pourquoi ?** Parce que vous vouliez **juste tester les prompts** ! 🎯

---

## 🔄 Prochaines Étapes (Quand Vous Serez Prêt)

Après avoir validé que les prompts fonctionnent bien :

1. Ajuster les requêtes si nécessaire
2. Modifier les seuils de confiance
3. Tester avec différents articles
4. **PUIS** implémenter dans LangGraph (si souhaité)

---

## 🆘 Support

Le script affiche des erreurs claires si quelque chose ne va pas :
- Clés API manquantes
- Erreurs Tavily
- Exceptions Python

---

**C'est simple, c'est direct, ça teste juste ce que vous vouliez tester !** ✅
