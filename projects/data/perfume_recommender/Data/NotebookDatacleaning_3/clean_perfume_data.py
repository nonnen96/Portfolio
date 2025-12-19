import pandas as pd
import re

# Fonction pour nettoyer le nom du parfum
def clean_perfume_name(perfume_name, brand_name):
    """Supprime la marque et les mentions 'for men', 'for women', 'and men', 'and women'."""
    if not isinstance(perfume_name, str) or not isinstance(brand_name, str):
        print(f"Valeurs inattendues : Perfume='{perfume_name}', Brand='{brand_name}'")
        return perfume_name  # Retourne tel quel si ce n'est pas une chaîne

    # Nettoyer le nom du parfum
    perfume_name = perfume_name.replace(brand_name, '').strip()  # Supprimer la marque
    perfume_name = re.sub(r'(\s+and\s+(men|women))', '', perfume_name).strip()  # Supprimer 'and men' ou 'and women'
    perfume_name = re.sub(r' for (men|women|men and women|women and men)', '', perfume_name).strip()  # Supprimer 'for ...'
    return perfume_name

# Fonction pour extraire le genre
def extract_gender(perfume_name):
    """Extrait le genre (Men, Women, Unisex, Unknown) depuis le nom du parfum."""
    if not isinstance(perfume_name, str):
        return "Unknown"
    perfume_name_lower = perfume_name.lower()
    if "for women and men" in perfume_name_lower or "for men and women" in perfume_name_lower:
        return "Unisex"
    elif "for men" in perfume_name_lower:
        return "Men"
    elif "for women" in perfume_name_lower:
        return "Women"
    else:
        return "Unknown"

# Fonction principale pour nettoyer les données
def clean_perfume_data(input_file, output_file):
    """
    Nettoie les données de parfums en supprimant les doublons et les lignes avec des valeurs 'Non disponible'.
    """
    # Charger les données depuis le fichier Excel
    df = pd.read_excel(input_file)

    # Remplacer les valeurs manquantes par des chaînes vides
    df['Perfume'] = df['Perfume'].fillna("Non disponible").astype(str)
    df['Brand'] = df['Brand'].fillna("Non disponible").astype(str)

    # Ajouter une colonne 'Gender' en extrayant le genre
    df['Gender'] = df['Perfume'].apply(extract_gender)

    # Nettoyer la colonne 'Perfume'
    df['Perfume'] = df.apply(
        lambda row: clean_perfume_name(row['Perfume'], row['Brand']), axis=1
    )

    # Supprimer les lignes contenant 'Non disponible'
    df_cleaned = df[~df.isin(['Non disponible']).any(axis=1)]

    # Supprimer les doublons basés sur 'Brand' et 'Perfume'
    df_cleaned = df_cleaned.drop_duplicates(subset=['Brand', 'Perfume'], keep='first')

    # Enregistrer les données nettoyées et sans doublons dans un nouveau fichier Excel
    df_cleaned.to_excel(output_file, index=False)
    print(f"Données nettoyées et sans doublons enregistrées dans : {output_file}")
