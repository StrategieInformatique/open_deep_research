# 🔄 Compatibilité Optimia_v2

## ✅ ArticlePayload - 100% Compatible

L'`ArticlePayload` est maintenant **100% compatible** avec `ProductStateInput` d'Optimia_v2.

### Tous les Champs Optimia_v2 Supportés

```python
class ArticlePayload(BaseModel):
    # ========== Identifiants ==========
    assistant_id: str = "product_description_crafter"
    ident: str                          # ID unique article
    ean: str                            # Code EAN

    # ========== Données produit ==========
    libelle: str                        # Nom produit
    marque: str                         # Marque
    description: str                    # Description existante
    instructions: str                   # Instructions

    # ========== Fournisseur ==========
    refFournisseur: Optional[str]       # Référence fournisseur
    fournisseur: Optional[str]          # Code fournisseur
    lib_fournisseur: Optional[str]      # Nom fournisseur

    # ========== Classification ==========
    famille: Optional[str]              # Code famille
    lib_famille: Optional[str]          # Libellé famille

    # ========== Attributs physiques ==========
    arcoul: str                         # Couleur
    coll: str                           # Collection
    dimensions: str                     # Dimensions

    # ========== URLs et médias ==========
    url: str                            # URL produit
    images_url: Optional[str]           # URL images
    file_url: Optional[str]             # URL fichier

    # ========== Propriétés personnalisées ==========
    nompropr: str                       # Nom propriété
    valpropr: str                       # Valeur propriété

    # ========== Métadonnées ==========
    craft_try: int                      # Nb tentatives craft
    prixttc: Optional[float]            # Prix TTC
    profilFamille: Optional[Dict]       # Profil famille

    # ========== Champs additionnels enrichissement ==========
    images_urls: List[str]              # Liste URLs images
    fiche_technique_url: Optional[str]  # URL fiche technique
    documents_techniques: Optional[Dict] # Documents techniques
    specifications_techniques: Optional[Dict] # Specs techniques
```

---

## 🔁 Rétrocompatibilité avec Ancien Format

### Alias Automatiques

Les anciennes propriétés sont accessibles via des **alias** :

```python
article_payload.article_id          # → ident
article_payload.reference_fournisseur # → refFournisseur
article_payload.famille_produit      # → famille
article_payload.images_disponibles   # → property (images_url or images_urls)
```

### Mapping Automatique dans write_research_brief

```python
# Ancien format → Nouveau format (automatique)
if 'article_id' in data and 'ident' not in data:
    data['ident'] = data['article_id']
if 'reference_fournisseur' in data and 'refFournisseur' not in data:
    data['refFournisseur'] = data['reference_fournisseur']
if 'famille_produit' in data and 'famille' not in data:
    data['famille'] = data['famille_produit']
```

---

## 📝 Exemples d'Input

### Format Optimia_v2 (Recommandé)

```json
{
  "messages": [
    {
      "role": "user",
      "content": "{\"assistant_id\": \"product_description_crafter\", \"ident\": \"DELO-IS2144BK\", \"ean\": \"8021098280152\", \"libelle\": \"CENTRALE VAPEUR IS2144BK NOIR BRAUN\", \"marque\": \"BRAUN\", \"description\": \"\", \"instructions\": \"\", \"refFournisseur\": \"IS2144BK\", \"fournisseur\": \"DELO\", \"lib_fournisseur\": \"Delonghi\", \"famille\": \"ELEC\", \"lib_famille\": \"Electroménager\", \"arcoul\": \"NOIR\", \"coll\": \"\", \"dimensions\": \"30x20x15cm\", \"url\": \"\", \"images_url\": \"https://example.com/images/DELO-IS2144BK/\", \"file_url\": null, \"nompropr\": \"\", \"valpropr\": \"\", \"craft_try\": 0, \"prixttc\": 179.99, \"profilFamille\": null}"
    }
  ]
}
```

### Format Ancien (Compatible avec mapping automatique)

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

Les deux formats fonctionnent ! Le mapping est automatique.

---

## 🔍 Détection Automatique

Le système détecte automatiquement si c'est un article en cherchant :
- `ident` (Optimia_v2)
- `article_id` (ancien format)
- `ean` (les deux formats)
- `libelle` (les deux formats)

---

## 📊 Output JSON Enrichi

Le JSON retourné inclut maintenant **toutes les métadonnées Optimia_v2** :

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

## ✅ Tests de Compatibilité

### Test 1 : Format Optimia_v2 Complet

```python
from open_deep_research.state import ArticlePayload

article = ArticlePayload(
    ident='DELO-IS2144BK',
    libelle='CENTRALE VAPEUR IS2144BK NOIR BRAUN',
    marque='BRAUN',
    ean='8021098280152',
    refFournisseur='IS2144BK',
    famille='ELEC',
    lib_famille='Electroménager',
    arcoul='NOIR',
    prixttc=179.99
)

# ✅ OK
assert article.ident == 'DELO-IS2144BK'
assert article.article_id == 'DELO-IS2144BK'  # Alias
assert article.refFournisseur == 'IS2144BK'
assert article.reference_fournisseur == 'IS2144BK'  # Alias
```

### Test 2 : Format Ancien avec Mapping

```python
data = {
    'article_id': 'TEST-123',
    'libelle': 'TEST PRODUCT',
    'marque': 'TEST',
    'reference_fournisseur': 'REF-001',
    'famille_produit': 'CAT-01'
}

# Mapping automatique
if 'article_id' in data and 'ident' not in data:
    data['ident'] = data['article_id']
if 'reference_fournisseur' in data and 'refFournisseur' not in data:
    data['refFournisseur'] = data['reference_fournisseur']
if 'famille_produit' in data and 'famille' not in data:
    data['famille'] = data['famille_produit']

article = ArticlePayload(**data)

# ✅ OK
assert article.ident == 'TEST-123'
assert article.article_id == 'TEST-123'
assert article.refFournisseur == 'REF-001'
assert article.famille == 'CAT-01'
```

### Test 3 : Property images_disponibles

```python
# Avec images_url
a1 = ArticlePayload(ident='TEST', libelle='Test', images_url='https://example.com/img.jpg')
assert a1.images_disponibles == True  # ✅

# Avec images_urls
a2 = ArticlePayload(ident='TEST', libelle='Test', images_urls=['https://example.com/img1.jpg'])
assert a2.images_disponibles == True  # ✅

# Sans images
a3 = ArticlePayload(ident='TEST', libelle='Test')
assert a3.images_disponibles == False  # ✅
```

---

## 🚀 Migration depuis Optimia_v2

Si vous avez des webhooks ou scripts qui envoient des données au format `ProductStateInput`, **aucune modification n'est nécessaire** !

Le système accepte directement :
- ✅ Tous les champs Optimia_v2
- ✅ Les mêmes noms de champs (ident, refFournisseur, arcoul, etc.)
- ✅ Le même format JSON

### Exemple de Migration

**Avant (Optimia_v2)** :
```python
# Dans votre webhook
payload = {
    "ident": article.id,
    "ean": article.ean,
    "libelle": article.libelle,
    "marque": article.marque,
    # ... tous les champs Optimia_v2
}
```

**Après (Open Deep Research)** :
```python
# EXACTEMENT le même payload !
payload = {
    "ident": article.id,
    "ean": article.ean,
    "libelle": article.libelle,
    "marque": article.marque,
    # ... tous les champs Optimia_v2
}
```

**Pas de changement nécessaire !** ✅

---

## 📋 Checklist Migration

- [x] ArticlePayload avec tous les champs Optimia_v2
- [x] Alias pour rétrocompatibilité (article_id, reference_fournisseur, famille_produit)
- [x] Property images_disponibles
- [x] Mapping automatique ancien → nouveau format
- [x] Detection automatique du format
- [x] Output JSON avec métadonnées Optimia_v2 complètes
- [x] Tests de compatibilité passants

---

## 🎉 Conclusion

Le système est **100% compatible** avec Optimia_v2 tout en restant rétrocompatible avec l'ancien format !

Vous pouvez :
- ✅ Utiliser directement le format Optimia_v2 (recommandé)
- ✅ Utiliser l'ancien format (mapping automatique)
- ✅ Mixer les deux formats (détection automatique)

Aucune régression, compatibilité totale ! 🚀
