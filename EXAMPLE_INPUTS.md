# 📝 Exemples d'Input pour LangGraph Studio

## Format Optimia_v2 (Recommandé)

### Exemple 1 : Centrale Vapeur BRAUN (Complet)

```json
{
  "messages": [
    {
      "role": "user",
      "content": "{\"assistant_id\": \"product_description_crafter\", \"ident\": \"DELO-IS2144BK\", \"ean\": \"8021098280152\", \"libelle\": \"CENTRALE VAPEUR IS2144BK NOIR BRAUN\", \"marque\": \"BRAUN\", \"description\": \"\", \"instructions\": \"\", \"refFournisseur\": \"IS2144BK\", \"fournisseur\": \"DELO\", \"lib_fournisseur\": \"Delonghi\", \"famille\": \"ELEC\", \"lib_famille\": \"Electroménager\", \"arcoul\": \"NOIR\", \"coll\": \"\", \"dimensions\": \"30x20x15cm\", \"url\": \"\", \"images_url\": \"https://hiyciqitdagwmudapohf.supabase.co/storage/v1/object/public/associmages/MCC/articlesImg/DELO-IS2144BK/\", \"file_url\": null, \"nompropr\": \"\", \"valpropr\": \"\", \"craft_try\": 0, \"prixttc\": 179.99, \"profilFamille\": null}"
    }
  ]
}
```

**Résultat attendu** : `REFERENTIEL` (Amazon trouvé avec ASIN)

---

### Exemple 2 : Fer à Repasser ARIETE

```json
{
  "messages": [
    {
      "role": "user",
      "content": "{\"assistant_id\": \"product_description_crafter\", \"ident\": \"ARIE-623500\", \"ean\": \"8003705114265\", \"libelle\": \"FER A REP. 6235/00 POURPE ARIETE\", \"marque\": \"ARIETE\", \"description\": \"\", \"instructions\": \"\", \"refFournisseur\": \"623500\", \"fournisseur\": \"ARIE\", \"lib_fournisseur\": \"Ariete\", \"famille\": \"ELEC\", \"lib_famille\": \"Petit Electroménager\", \"arcoul\": \"POURPRE\", \"coll\": \"\", \"dimensions\": \"\", \"url\": \"\", \"images_url\": null, \"file_url\": null, \"nompropr\": \"\", \"valpropr\": \"\", \"craft_try\": 0, \"prixttc\": 39.99, \"profilFamille\": null}"
    }
  ]
}
```

**Résultat attendu** : `REFERENTIEL` ou `WEB`

---

### Exemple 3 : Tablette VANKYO (Difficile à trouver)

```json
{
  "messages": [
    {
      "role": "user",
      "content": "{\"assistant_id\": \"product_description_crafter\", \"ident\": \"ARCO-RIOPAD7NOIR\", \"ean\": \"3483072500598\", \"libelle\": \"VANKYO MATRIXPAD S8 TABLETTE TACTILE 8 POUCES\", \"marque\": \"VANKYO\", \"description\": \"\", \"instructions\": \"\", \"refFournisseur\": \"MATRIXPAD-S8\", \"fournisseur\": \"ARCO\", \"lib_fournisseur\": \"Arcotrade\", \"famille\": \"INFO\", \"lib_famille\": \"Informatique\", \"arcoul\": \"NOIR\", \"coll\": \"\", \"dimensions\": \"8 pouces\", \"url\": \"\", \"images_url\": \"https://example.com/images/\", \"file_url\": null, \"nompropr\": \"systeme\", \"valpropr\": \"Android 10.0\", \"craft_try\": 0, \"prixttc\": 99.99, \"profilFamille\": null}"
    }
  ]
}
```

**Résultat attendu** : `WEB` ou `GENERATIF`

---

## Format Ancien (Rétrocompatible)

### Exemple 4 : Centrale Vapeur BRAUN (Format Ancien)

```json
{
  "messages": [
    {
      "role": "user",
      "content": "{\"article_id\": \"DELO-IS2144BK\", \"libelle\": \"CENTRALE VAPEUR IS2144BK NOIR BRAUN\", \"marque\": \"BRAUN\", \"ean\": \"8021098280152\", \"reference_fournisseur\": \"IS2144BK\", \"famille_produit\": \"CENTRALE VAPEUR\", \"images_disponibles\": true, \"images_urls\": [\"https://example.com/image.jpg\"], \"specifications_techniques\": {\"couleur\": \"Noir\", \"prix_ttc\": 179.99}}"
    }
  ]
}
```

**Note** : Le mapping automatique convertit :
- `article_id` → `ident`
- `reference_fournisseur` → `refFournisseur`
- `famille_produit` → `famille`

---

## Format Minimal (Pour Tests Rapides)

### Exemple 5 : Minimal avec EAN

```json
{
  "messages": [
    {
      "role": "user",
      "content": "{\"ident\": \"TEST-001\", \"libelle\": \"BRAUN IS2144BK CENTRAL VAPEUR\", \"marque\": \"BRAUN\", \"ean\": \"8021098280152\"}"
    }
  ]
}
```

---

### Exemple 6 : Minimal sans EAN

```json
{
  "messages": [
    {
      "role": "user",
      "content": "{\"ident\": \"TEST-002\", \"libelle\": \"ARIETE FER A REPASSER 6235\", \"marque\": \"ARIETE\", \"refFournisseur\": \"623500\"}"
    }
  ]
}
```

---

## JSON Formaté (Plus Lisible)

Pour éditer dans un éditeur JSON, utilisez ce format :

```json
{
  "messages": [
    {
      "role": "user",
      "content": "{\"assistant_id\": \"product_description_crafter\", \"ident\": \"DELO-IS2144BK\", \"ean\": \"8021098280152\", \"libelle\": \"CENTRALE VAPEUR IS2144BK NOIR BRAUN\", \"marque\": \"BRAUN\", \"description\": \"\", \"instructions\": \"\", \"refFournisseur\": \"IS2144BK\", \"fournisseur\": \"DELO\", \"lib_fournisseur\": \"Delonghi\", \"famille\": \"ELEC\", \"lib_famille\": \"Electroménager\", \"arcoul\": \"NOIR\", \"coll\": \"\", \"dimensions\": \"30x20x15cm\", \"url\": \"\", \"images_url\": \"https://example.com/images/\", \"file_url\": null, \"nompropr\": \"\", \"valpropr\": \"\", \"craft_try\": 0, \"prixttc\": 179.99, \"profilFamille\": null}"
    }
  ]
}
```

---

## 🔧 Configuration LangGraph Studio

### Paramètres Recommandés

Dans l'UI LangGraph Studio, configurez :

```yaml
allow_clarification: false
search_api: "tavily"
max_amazon_searches: 3
max_web_searches: 3
tavily_search_depth: "advanced"
tavily_max_results: 10

# Seuils de confiance
referentiel_min_confidence: 0.75
web_min_confidence: 0.60
generatif_min_confidence: 0.50
min_web_sources: 2

# Domaines Amazon
amazon_domains:
  - amazon.fr
  - amazon.it
  - amazon.com
  - amazon.es
  - amazon.de
  - amazon.co.uk
```

---

## 📊 Output Attendu

Le système retourne un JSON avec :

```json
{
  "enrichment_type": "REFERENTIEL",
  "confidence_score": 0.85,
  "justification": "Found 1 Amazon product(s) with ASIN",
  "next_subgraph": "amazon_subgraph",
  "amazon_products": [
    {
      "asin": "B0XXXXXXXX",
      "domain": "amazon.fr",
      "url": "https://www.amazon.fr/dp/B0XXXXXXXX",
      "title": "Product B0XXXXXXXX",
      "score": 0.85
    }
  ],
  "web_sources": [],
  "search_summary": {
    "total_findings": 5,
    "amazon_results": 1,
    "web_results": 0,
    "ident": "DELO-IS2144BK",
    "article_id": "DELO-IS2144BK",
    "ean": "8021098280152",
    "libelle": "CENTRALE VAPEUR IS2144BK NOIR BRAUN",
    "marque": "BRAUN",
    "famille": "ELEC",
    "lib_famille": "Electroménager"
  }
}
```

---

## 🚀 Comment Utiliser

### 1. Lancer LangGraph Studio

```bash
cd /Users/devopsstudio/Repoz/pro/open_deep_research
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev --allow-blocking
```

### 2. Ouvrir dans le Navigateur

Accéder à : https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

### 3. Sélectionner le Graph

Choisir : **"Deep Researcher"**

### 4. Coller l'Input JSON

Copier-coller un des exemples ci-dessus dans le champ d'input.

### 5. Configurer les Variables d'Environnement

Créer un fichier `.env` :
```bash
TAVILY_API_KEY=tvly-votre-clé
OPENAI_API_KEY=sk-votre-clé
```

### 6. Exécuter

Cliquer sur "Run" et observer les logs dans le terminal.

---

## 🎯 Cas d'Usage

### Test Amazon Search
Utiliser **Exemple 1** (Centrale Vapeur BRAUN) qui a un EAN valide et devrait être trouvé sur Amazon.

### Test Web Search
Utiliser **Exemple 3** (Tablette VANKYO) avec un EAN difficile à trouver.

### Test Generatif
Utiliser un produit avec `images_url` mais sans EAN ou avec EAN introuvable.

### Test Migration Optimia_v2
Utiliser **Exemple 1** au format Optimia_v2 complet pour valider la compatibilité.

---

## ⚠️ Troubleshooting

### Erreur "article_payload not found"
➜ Vérifiez le format JSON (doit être stringifié dans `content`)

### Résultat générique sur "Research Questions"
➜ Vérifiez que le graph "Deep Researcher" est bien sélectionné

### "TAVILY_API_KEY not set"
➜ Créez un fichier `.env` avec votre clé Tavily

### Pas de produits Amazon trouvés
➜ Vérifiez que l'EAN est correct et que le produit existe sur Amazon

---

**Bon test !** 🚀
