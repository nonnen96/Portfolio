import pandas as pd
import plotly.express as px
from sklearn.manifold import TSNE
from sentence_transformers import SentenceTransformer
import torch

def load_and_prepare_data_by_brands(file_path, brands_filter=None, sample_size=100):
    """
    Charge les données, filtre par plusieurs marques et prépare les colonnes pertinentes.
    """
    df = pd.read_excel(file_path)
    
    # Filtrer par plusieurs marques si spécifié
    if brands_filter:
        df = df[df['Brand'].str.contains('|'.join(brands_filter), case=False, na=False)]

    # Remplacer les valeurs manquantes dans les accords principaux
    df['Main Accords'] = df['Main Accords'].fillna('')

    # Supprimer les lignes où les accords principaux sont absents ou 'Non disponible'
    df = df[df['Main Accords'] != 'Non Disponible']

    # Ajouter une colonne concaténant les accords principaux
    df['accords_concatenes'] = df['Main Accords']

    # Limiter à un échantillon si nécessaire
    if len(df) > sample_size:
        df = df.sample(sample_size, random_state=42).reset_index(drop=True)
    return df

def load_or_compute_embeddings(df, save_path="embeddings.pt"):
    """
    Charge les embeddings pré-calculés ou les calcule si absents.
    """
    try:
        saved_data = torch.load(save_path)
        embeddings = saved_data[1] if isinstance(saved_data, tuple) else saved_data
        print(f"Embeddings chargés depuis {save_path}.")
    except FileNotFoundError:
        print("Aucun fichier d'embeddings trouvé. Calcul en cours...")
        model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        embeddings = model.encode(df['accords_concatenes'].tolist(), batch_size=32, convert_to_tensor=False)
        torch.save((df, embeddings), save_path)
        print(f"Embeddings sauvegardés dans {save_path}.")
    return embeddings

def reduce_dimension(embeddings, n_components=2):
    """
    Réduit la dimensionnalité des vecteurs avec t-SNE pour la visualisation.
    """
    perplexity = min(30, len(embeddings) - 1)
    print(f"Perplexité ajustée à : {perplexity}")
    tsne = TSNE(n_components=n_components, perplexity=perplexity, random_state=42)
    reduced_embeddings = tsne.fit_transform(embeddings)
    return reduced_embeddings

def plot_interactive_olfactory_map(embeddings_2d, df, brands_filter):
    """
    Crée une carte olfactive interactive avec Plotly, avec des couleurs basées sur le genre.
    """
    # Ajouter les dimensions réduites au DataFrame
    df['Dimension 1'] = embeddings_2d[:, 0]
    df['Dimension 2'] = embeddings_2d[:, 1]

    # Mapper les genres à des couleurs spécifiques
    color_map = {"Men": "blue", "Women": "pink", "Unisex": "gray"}
    df['Color'] = df['Gender'].map(color_map).fillna("gray")  # Défaut gris pour les valeurs manquantes

    # Créer une carte interactive avec Plotly
    fig = px.scatter(
        df,
        x="Dimension 1",
        y="Dimension 2",
        color="Brand",  # Couleurs basées sur les marques
        hover_data=["Perfume", "Main Accords", "Gender"],  # Afficher les détails au survol
        title=f"Carte Olfactive Interactive - Marques : {', '.join(brands_filter)}",
        labels={"Brand": "Marque", "Gender": "Genre"},
        size_max=15
    )

    # Modifier l'esthétique de la légende et des axes
    fig.update_layout(
        legend_title="Marques",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        title={
            'text': f"Carte Olfactive Interactive - Marques : {', '.join(brands_filter)}",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis=dict(title="Dimension 1", showgrid=True, zeroline=True),
        yaxis=dict(title="Dimension 2", showgrid=True, zeroline=True),
        plot_bgcolor="white"
    )

    # Afficher la carte interactive
    fig.show()

def main():
    file_path = "perfume_data_cleaned.xlsx"
    brands_filter = ["Dior", "Tom Ford", "Maison Francis Kurkdjian"]  # Liste des marques à inclure
    save_path = "embeddings_combined.pt"
    sample_size = 200  # Limiter à 200 échantillons pour une meilleure lisibilité

    print(f"Chargement des données pour les marques : {', '.join(brands_filter)}...")
    df = load_and_prepare_data_by_brands(file_path, brands_filter=brands_filter, sample_size=sample_size)

    print("Chargement ou calcul des embeddings...")
    embeddings = load_or_compute_embeddings(df, save_path)

    print(f"Dimensions des embeddings avant réduction : {len(embeddings)}")
    embeddings_2d = reduce_dimension(embeddings)

    print(f"Visualisation de la carte olfactive pour les marques : {', '.join(brands_filter)}...")
    plot_interactive_olfactory_map(embeddings_2d, df, brands_filter)