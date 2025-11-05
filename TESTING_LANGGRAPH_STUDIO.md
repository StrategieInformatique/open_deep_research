# 🧪 Guide de Test - LangGraph Studio

## ✅ Système de Logging Ajouté

Le système d'enrichissement dispose maintenant d'un **système de logging structuré** dans le terminal, similaire à votre projet Optimia_v2.

### Fichiers de Logging Créés

1. **`src/open_deep_research/utils/logger_config.py`**
   - Configuration centralisée du logging
   - Loggers spécialisés (enrichment, deep_researcher, subgraphs, tavily)
   - Réduction du bruit des bibliothèques tierces

2. **`src/open_deep_research/utils/log_helpers.py`**
   - Fonctions helper pour logs structurés
   - Emojis et séparateurs visuels
   - Logs détaillés pour chaque phase

3. **`src/open_deep_research/article_enrichment_graph_v2.py`** ✨ NOUVEAU
   - Version du graph avec logging intégré
   - Logs détaillés à chaque étape

---

## 🔧 Configuration LangGraph Studio

### 1. Vérifier le Graph Chargé

Dans LangGraph Studio, assurez-vous de sélectionner **"Article Enrichment"** dans la liste des graphs.

Le `langgraph.json` a été mis à jour pour exposer le graph :
```json
{
  "graphs": {
    "Deep Researcher": "./src/open_deep_research/deep_researcher.py:deep_researcher",
    "Article Enrichment": "./src/open_deep_research/article_enrichment_graph_v2.py:enrichment_graph"
  }
}
```

---

## 📝 Format d'Input pour LangGraph Studio

### ⚠️ IMPORTANT : Structure de l'Input

LangGraph Studio requiert un format spécifique. Votre input doit être structuré comme ceci :

```json
{
  "article_payload": {
    "article_id": "DELO-IS2144BK",
    "libelle": "CENTRALE VAPEUR IS2144BK NOIR BRAUN",
    "marque": "BRAUN",
    "ean": "8021098280152",
    "reference_fournisseur": "IS2144BK",
    "famille_produit": "CENTRALE VAPEUR",
    "images_disponibles": true,
    "images_urls": ["https://hiyciqitdagwmudapohf.supabase.co/storage/v1/object/public/associmages/MCC/articlesImg/DELO-IS2144BK/0066453301AE436F4F300BD001_placeholder.png"],
    "specifications_techniques": {
      "couleur": "Noir",
      "prix_ttc": 179.99
    }
  }
}
```

### ❌ Ce Qui ne Fonctionnera PAS

Ne pas envoyer directement le payload de votre webhook :
```json
{
  "body": {
    "payload": "{\"ean\":\"8021098280152\"...}"
  }
}
```

Le graph attend un objet `article_payload` directement, pas un JSON stringifié dans `body.payload`.

---

## 🧪 Requêtes de Test

### Test 1 : Centrale Vapeur BRAUN (Amazon)

```json
{
  "article_payload": {
    "article_id": "DELO-IS2144BK",
    "libelle": "CENTRALE VAPEUR IS2144BK NOIR BRAUN",
    "marque": "BRAUN",
    "ean": "8021098280152",
    "reference_fournisseur": "IS2144BK",
    "famille_produit": "CENTRALE VAPEUR",
    "images_disponibles": true,
    "images_urls": ["https://example.com/image.jpg"],
    "fiche_technique_url": null,
    "documents_techniques": null,
    "specifications_techniques": {
      "couleur": "Noir",
      "prix_ttc": 179.99
    }
  }
}
```

**Résultat attendu** : `REFERENTIEL` (Amazon trouvé avec ASIN)

---

### Test 2 : Fer à Repasser ARIETE (Web)

```json
{
  "article_payload": {
    "article_id": "ARIE-623500",
    "libelle": "FER A REP. 6235/00 POURPE ARIETE",
    "marque": "ARIETE",
    "ean": "8003705114265",
    "reference_fournisseur": "623500",
    "famille_produit": "FER À REPASSER",
    "images_disponibles": true,
    "images_urls": ["https://example.com/image.jpg"],
    "fiche_technique_url": null,
    "documents_techniques": null,
    "specifications_techniques": {
      "prix_ttc": 39.99
    }
  }
}
```

**Résultat attendu** : `WEB` ou `REFERENTIEL` selon disponibilité

---

### Test 3 : Tablette VANKYO (Difficile à trouver)

```json
{
  "article_payload": {
    "article_id": "ARCO-RIOPAD7NOIR",
    "libelle": "VANKYO MATRIXPAD S8 TABLETTE TACTILE 8 POUCES",
    "marque": "VANKYO",
    "ean": "3483072500598",
    "reference_fournisseur": "MATRIXPAD-S8",
    "famille_produit": "TABLETTE TACTILE",
    "images_disponibles": true,
    "images_urls": ["https://example.com/image.jpg"],
    "fiche_technique_url": null,
    "documents_techniques": null,
    "specifications_techniques": {
      "taille_ecran": "8 pouces",
      "systeme": "Android 10.0",
      "prix_ttc": 99.99
    }
  }
}
```

**Résultat attendu** : `WEB` ou `GENERATIF`

---

## 📊 Logs dans le Terminal

Avec le nouveau système de logging, vous verrez dans le terminal :

```
==================================================
🔵 [NODE_ENTRY] create_research_brief
  📦 Article: BRAUN CENTRALE VAPEUR IS2144BK NOIR BRAUN
  🔢 EAN: 8021098280152
==================================================

==================================================
[ARTICLE_INFO] Informations produit
  📦 Produit: CENTRALE VAPEUR IS2144BK NOIR BRAUN
  🏷️  Marque: BRAUN
  🔢 EAN: 8021098280152
  📋 Réf Fournisseur: IS2144BK
  📂 Catégorie: CENTRALE VAPEUR
  🖼️  Images: ✅ (1)
  ⚙️  Specs techniques: ✅
==================================================

📝 [BRIEF_CREATION] Génération du brief de recherche
  • Requêtes générées: 8
    - universal: 2 requêtes
    - french: 2 requêtes
    - english: 2 requêtes
    - italian: 1 requêtes

✅ [NODE_EXIT] create_research_brief
  ➡️  Next: deep_researcher

==================================================
🔵 [NODE_ENTRY] deep_researcher
  📦 Article: BRAUN CENTRALE VAPEUR IS2144BK NOIR BRAUN
  🔢 EAN: 8021098280152
==================================================

--------------------------------------------------
🔍 [PHASE 1] Recherche Amazon Multi-pays
  📝 Nombre de requêtes: 3
    1. 8021098280152 amazon
    2. BRAUN IS2144BK amazon
    3. BRAUN CENTRALE VAPEUR amazon
--------------------------------------------------

✅ [PHASE 1] Recherche Amazon terminée
  ✅ 1 produit(s) Amazon trouvé(s)
    1. ASIN: B0XXXXXXXX
       Domain: amazon.fr
       URL: https://www.amazon.fr/dp/B0XXXXXXXX
       Title: Braun IS2144BK Centrale Vapeur...

🎯 [DECISION] 1 produit(s) Amazon trouvé(s)
📊 [CONFIDENCE] Score calculé: 0.50
✅ [ROUTING] Confidence 0.50 >= 0.75
➡️  [ROUTING] Direction: REFERENTIEL (Amazon)

==================================================
🎯 [ROUTING_DECISION] Décision de routage
  📍 Type d'enrichissement: REFERENTIEL
  📊 Score de confiance: 0.50
  📝 Justification: Product found on Amazon...
  🛒 Produits Amazon: 1
     • ASIN: B0XXXXXXXX (amazon.fr)
  🔍 Résumé recherche:
     • Phase: Amazon
     • Requêtes: 3
     • Résultats: 1
     • Langues: universal, english, french
==================================================

✅ [NODE_EXIT] deep_researcher
  ➡️  Next: amazon_subgraph

==================================================
🔵 [NODE_ENTRY] amazon_subgraph (STUB)
==================================================
📦 [STUB] Amazon Subgraph - À implémenter
✅ [NODE_EXIT] amazon_subgraph
  ➡️  Next: output_results

==================================================
📋 [FINAL_SUMMARY] Résumé du traitement
  🎯 Type: REFERENTIEL
  📊 Confiance: 0.50
  📌 Statut: STUB_REFERENTIEL
  ⏱️  Durée totale: 5.23s
  🔄 Itérations de recherche: 3
==================================================
```

---

## 🐛 Problèmes Courants

### 1. Résultat Générique sur "Research Questions"

**Cause** : Le graph "Deep Researcher" a été chargé au lieu de "Article Enrichment"

**Solution** :
1. Dans LangGraph Studio, sélectionnez le graph **"Article Enrichment"**
2. Vérifiez que l'URL indique `.../Article%20Enrichment/...`

---

### 2. Erreur "article_payload not found"

**Cause** : Format d'input incorrect

**Solution** : Assurez-vous que votre JSON commence par `{"article_payload": {...}}`

---

### 3. Pas de Logs Visibles

**Cause** : Console de LangGraph Studio peut ne pas afficher tous les logs

**Solution** :
- Utilisez le terminal en parallèle avec `langgraph dev`
- Vérifiez les logs dans l'onglet "Logs" de LangGraph Studio

---

### 4. "TAVILY_API_KEY not set"

**Solution** :
1. Créer un fichier `.env` à la racine du projet
2. Ajouter :
   ```
   TAVILY_API_KEY=tvly-votre-clé
   OPENAI_API_KEY=sk-votre-clé
   ```

---

## 🚀 Prochaines Étapes

Après avoir validé que le `deep_researcher` fonctionne correctement avec vos vraies données :

1. **Ajuster les seuils** si nécessaire dans `configuration_enrichment.py`
2. **Implémenter les subgraphs** :
   - `amazon_subgraph` (REFERENTIEL)
   - `web_subgraph` (WEB)
   - `generative_subgraph` (GENERATIF)
3. **Remplacer `output_results`** par `report_generator` complet

---

## 📖 Documentation Complète

- **`ENRICHMENT_QUICKSTART.md`** : Guide de démarrage
- **`ENRICHMENT_SETUP.md`** : Architecture détaillée
- **`IMPLEMENTATION_SUMMARY.md`** : Ce qui a été implémenté

---

## ✅ Checklist de Test

- [ ] Graph "Article Enrichment" sélectionné dans LangGraph Studio
- [ ] Variables d'environnement (TAVILY_API_KEY, OPENAI_API_KEY) définies
- [ ] Format d'input correct : `{"article_payload": {...}}`
- [ ] Logs visibles dans le terminal
- [ ] Test avec centrale vapeur BRAUN
- [ ] Vérifier ASIN retourné
- [ ] Vérifier routing decision

---

**Bonne chance pour vos tests !** 🚀

Si vous avez des questions, consultez les logs détaillés dans le terminal.
