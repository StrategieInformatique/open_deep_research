#!/usr/bin/env python3
"""
Script pour générer des inputs JSON valides pour LangGraph Studio.

Usage:
    python generate_langgraph_input.py
"""

import json


def generate_input(article_data: dict) -> dict:
    """
    Génère un input valide pour LangGraph Studio.

    Args:
        article_data: Dictionnaire avec les données de l'article

    Returns:
        Input formaté pour LangGraph Studio
    """
    # Convertir l'article en JSON string (sur une seule ligne, pas de retours à la ligne)
    article_json_string = json.dumps(article_data, ensure_ascii=False, separators=(',', ':'))

    # Créer l'input pour LangGraph
    langgraph_input = {
        "messages": [
            {
                "role": "user",
                "content": article_json_string
            }
        ]
    }

    return langgraph_input


# ==========================================
# EXEMPLES D'ARTICLES
# ==========================================

# Exemple 1 : Format Optimia_v2 complet
article_optimia_v2 = {
    "assistant_id": "product_description_crafter",
    "ident": "DELO-IS2144BK",
    "ean": "8021098280152",
    "libelle": "CENTRALE VAPEUR IS2144BK NOIR BRAUN",
    "marque": "BRAUN",
    "description": "",
    "instructions": "",
    "refFournisseur": "IS2144BK",
    "fournisseur": "DELO",
    "lib_fournisseur": "Delonghi",
    "famille": "ELEC",
    "lib_famille": "Electroménager",
    "arcoul": "NOIR",
    "coll": "",
    "dimensions": "30x20x15cm",
    "url": "",
    "images_url": "https://hiyciqitdagwmudapohf.supabase.co/storage/v1/object/public/associmages/MCC/articlesImg/DELO-IS2144BK/",
    "file_url": None,
    "nompropr": "",
    "valpropr": "",
    "craft_try": 0,
    "prixttc": 179.99,
    "profilFamille": None
}

# Exemple 2 : Fer à repasser ARIETE
article_ariete = {
    "assistant_id": "product_description_crafter",
    "ident": "ARIE-623500",
    "ean": "8003705114265",
    "libelle": "FER A REP. 6235/00 POURPE ARIETE",
    "marque": "ARIETE",
    "description": "",
    "instructions": "",
    "refFournisseur": "623500",
    "fournisseur": "ARIE",
    "lib_fournisseur": "Ariete",
    "famille": "ELEC",
    "lib_famille": "Petit Electroménager",
    "arcoul": "POURPRE",
    "coll": "",
    "dimensions": "",
    "url": "",
    "images_url": None,
    "file_url": None,
    "nompropr": "",
    "valpropr": "",
    "craft_try": 0,
    "prixttc": 39.99,
    "profilFamille": None
}

# Exemple 3 : Format ancien (sera mappé automatiquement)
article_ancien_format = {
    "article_id": "TEST-001",
    "libelle": "CENTRALE VAPEUR TEST",
    "marque": "TESTBRAND",
    "ean": "1234567890123",
    "reference_fournisseur": "REF-001",
    "famille_produit": "ELEC"
}


if __name__ == "__main__":
    print("=" * 80)
    print("GÉNÉRATION D'INPUTS POUR LANGGRAPH STUDIO")
    print("=" * 80)
    print()

    # Générer les inputs
    examples = [
        ("Exemple 1: BRAUN Centrale Vapeur (Optimia_v2)", article_optimia_v2),
        ("Exemple 2: ARIETE Fer à Repasser", article_ariete),
        ("Exemple 3: Format Ancien (avec mapping)", article_ancien_format),
    ]

    for title, article in examples:
        print(f"\n{'=' * 80}")
        print(f"{title}")
        print(f"{'=' * 80}\n")

        # Générer l'input
        langgraph_input = generate_input(article)

        # Afficher en JSON formaté
        json_output = json.dumps(langgraph_input, indent=2, ensure_ascii=False)
        print(json_output)

        # Sauvegarder dans un fichier
        filename = f"input_{title.split(':')[0].replace(' ', '_').lower()}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json_output)

        print(f"\n✅ Sauvegardé dans: {filename}")

    print("\n" + "=" * 80)
    print("COMMENT UTILISER CES FICHIERS")
    print("=" * 80)
    print("""
1. Ouvrir LangGraph Studio
2. Sélectionner le graph "Deep Researcher"
3. Copier-coller le contenu d'un des fichiers JSON générés
4. Cliquer sur "Run"

⚠️  IMPORTANT :
   - Le JSON dans le champ "content" doit être sur UNE SEULE ligne
   - Pas de retours à la ligne dans le champ "content"
   - Les fichiers générés sont déjà au bon format
""")

    print("\n" + "=" * 80)
    print("CRÉER VOTRE PROPRE INPUT")
    print("=" * 80)
    print("""
import json

# Vos données article
mon_article = {
    "ident": "MON-ID",
    "libelle": "MON PRODUIT",
    "marque": "MA MARQUE",
    "ean": "1234567890123"
}

# Générer l'input
input_json = generate_input(mon_article)

# Afficher
print(json.dumps(input_json, indent=2, ensure_ascii=False))
""")
