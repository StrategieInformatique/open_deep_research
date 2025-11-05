# 🔧 Résolution de Problèmes LangGraph Studio

## ❌ Erreur: "Bad control character in string literal"

### Cause
Cette erreur survient quand le JSON dans le champ `content` contient des **caractères de contrôle** non échappés (retours à la ligne, tabulations, etc.).

### ❌ Mauvais Format (Avec Retours à Ligne)

```json
{
  "messages": [
    {
      "role": "user",
      "content": "{
        \"ident\": \"DELO-IS2144BK\",
        \"libelle\": \"CENTRALE VAPEUR\",
        \"marque\": \"BRAUN\"
      }"
    }
  ]
}
```

**Erreur** : Le JSON dans `content` a des retours à la ligne → ❌

---

### ✅ Bon Format (Une Seule Ligne)

```json
{
  "messages": [
    {
      "role": "user",
      "content": "{\"ident\":\"DELO-IS2144BK\",\"libelle\":\"CENTRALE VAPEUR\",\"marque\":\"BRAUN\"}"
    }
  ]
}
```

**Correct** : Le JSON dans `content` est sur une seule ligne → ✅

---

## 🛠️ Solutions

### Solution 1 : Utiliser les Fichiers Générés

3 fichiers JSON valides ont été générés pour vous :

```bash
input_exemple_1.json    # BRAUN Centrale Vapeur (format Optimia_v2)
input_exemple_2.json    # ARIETE Fer à Repasser
input_exemple_3.json    # Format ancien (avec mapping)
```

**Comment utiliser** :

1. Ouvrir le fichier JSON dans un éditeur de texte
2. Copier **TOUT** le contenu
3. Coller dans LangGraph Studio
4. Cliquer sur "Run"

---

### Solution 2 : Générer Votre Propre Input

Utiliser le script Python :

```bash
python generate_langgraph_input.py
```

Ou créer votre propre input :

```python
import json

# Vos données
article = {
    "ident": "MON-ID",
    "libelle": "MON PRODUIT",
    "marque": "MA MARQUE",
    "ean": "1234567890123"
}

# Générer l'input (sur une seule ligne automatiquement)
article_json_string = json.dumps(article, ensure_ascii=False, separators=(',', ':'))

langgraph_input = {
    "messages": [
        {
            "role": "user",
            "content": article_json_string
        }
    ]
}

# Afficher (copier-coller dans LangGraph Studio)
print(json.dumps(langgraph_input, indent=2, ensure_ascii=False))
```

---

### Solution 3 : Minifier le JSON Manuellement

Si vous avez un JSON formaté avec des retours à la ligne :

1. Aller sur https://jsonformatter.org/json-minifier
2. Coller votre JSON article
3. Cliquer sur "Minify"
4. Copier le résultat
5. L'utiliser dans le champ `content`

**Exemple** :

Avant (formaté) :
```json
{
  "ident": "TEST",
  "libelle": "PRODUIT",
  "marque": "MARQUE"
}
```

Après (minifié) :
```json
{"ident":"TEST","libelle":"PRODUIT","marque":"MARQUE"}
```

Puis utiliser dans LangGraph :
```json
{
  "messages": [
    {
      "role": "user",
      "content": "{\"ident\":\"TEST\",\"libelle\":\"PRODUIT\",\"marque\":\"MARQUE\"}"
    }
  ]
}
```

---

## 🎯 Format Final à Copier-Coller

### Exemple 1 : BRAUN Centrale Vapeur

```json
{
  "messages": [
    {
      "role": "user",
      "content": "{\"assistant_id\":\"product_description_crafter\",\"ident\":\"DELO-IS2144BK\",\"ean\":\"8021098280152\",\"libelle\":\"CENTRALE VAPEUR IS2144BK NOIR BRAUN\",\"marque\":\"BRAUN\",\"description\":\"\",\"instructions\":\"\",\"refFournisseur\":\"IS2144BK\",\"fournisseur\":\"DELO\",\"lib_fournisseur\":\"Delonghi\",\"famille\":\"ELEC\",\"lib_famille\":\"Electroménager\",\"arcoul\":\"NOIR\",\"coll\":\"\",\"dimensions\":\"30x20x15cm\",\"url\":\"\",\"images_url\":\"https://example.com/images/\",\"file_url\":null,\"nompropr\":\"\",\"valpropr\":\"\",\"craft_try\":0,\"prixttc\":179.99,\"profilFamille\":null}"
    }
  ]
}
```

### Exemple 2 : Format Minimal

```json
{
  "messages": [
    {
      "role": "user",
      "content": "{\"ident\":\"TEST-001\",\"libelle\":\"BRAUN CENTRALE VAPEUR\",\"marque\":\"BRAUN\",\"ean\":\"8021098280152\"}"
    }
  ]
}
```

---

## 🔍 Autres Erreurs Courantes

### Erreur: "Unexpected token"

**Cause** : JSON mal formé (virgule manquante, accolade non fermée, etc.)

**Solution** : Valider le JSON sur https://jsonlint.com/

---

### Erreur: "article_payload not found"

**Cause** : Le format d'input ne correspond pas

**Solution** : Vérifier que :
1. Le JSON est dans le champ `content`
2. Le JSON contient au moins `ident` ou `libelle`
3. Le format respecte la structure ci-dessus

---

### Erreur: "TAVILY_API_KEY not set"

**Cause** : Variable d'environnement manquante

**Solution** : Créer un fichier `.env` :
```bash
TAVILY_API_KEY=tvly-votre-clé
OPENAI_API_KEY=sk-votre-clé
```

---

## ✅ Checklist de Vérification

Avant de cliquer sur "Run" dans LangGraph Studio :

- [ ] Le graph "Deep Researcher" est sélectionné
- [ ] Le JSON est valide (pas d'erreur de syntaxe)
- [ ] Le champ `content` contient le JSON article **sur une seule ligne**
- [ ] Les variables d'environnement sont définies (`.env`)
- [ ] Le format inclut au minimum `ident` et `libelle`

---

## 📞 Debug

Pour débugger votre input :

```python
import json

# Votre input
input_text = '''COLLEZ VOTRE JSON ICI'''

# Valider
try:
    data = json.loads(input_text)
    print("✅ JSON valide")

    # Vérifier la structure
    if "messages" in data:
        print("✅ Champ 'messages' présent")
        if data["messages"][0]["content"]:
            print("✅ Champ 'content' présent")

            # Essayer de parser le content
            content = json.loads(data["messages"][0]["content"])
            print(f"✅ Content parsé: {content.get('ident', 'N/A')}")
    else:
        print("❌ Champ 'messages' manquant")

except json.JSONDecodeError as e:
    print(f"❌ JSON invalide: {e}")
```

---

## 🚀 Raccourci Rapide

**Pour tester rapidement** :

1. Ouvrir `input_exemple_1.json`
2. Copier TOUT le contenu
3. Coller dans LangGraph Studio
4. Run

C'est tout ! Aucune modification nécessaire. ✅
