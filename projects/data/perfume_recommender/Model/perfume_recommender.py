import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from torch.nn.functional import cosine_similarity
import numpy as np
import pickle
import numpy as np
import os 

def load_and_prepare_data(file_path):
    """
    Charge le fichier contenant les données de parfums et crée une colonne concaténée pour l'encodage.
    """
    df = pd.read_excel(file_path)
    df['texte_concatene'] = (
        df['Perfume'] + ". " +
        df['Description'].fillna('') +
        " Notes: " + df['Top Notes'].fillna('') + ", " +
        df['Middle Notes'].fillna('') + ", " +
        df['Base Notes'].fillna('') +
        df['Main Accords'].fillna('')
    )
    return df




def load_or_compute_embeddings(df, model, save_path="embeddings.pt"):
    """
    Charge ou calcule les embeddings des parfums. Sauvegarde uniquement les embeddings sous forme de tensor.
    """
    try:
        if os.path.exists(save_path):
            # Charger les embeddings directement
            embeddings = torch.load(save_path, map_location="cpu")
            if not isinstance(embeddings, torch.Tensor):
                raise ValueError("Le fichier d'embeddings contient des objets non supportés.")
            print(f"Embeddings chargés depuis {save_path}.")
        else:
            raise FileNotFoundError
    except (FileNotFoundError, ValueError):
        print("Aucun fichier d'embeddings valide trouvé. Calcul en cours...")
        # Calculer les embeddings
        embeddings = model.encode(df['texte_concatene'].tolist(), batch_size=32, convert_to_tensor=True)
        # Sauvegarder les embeddings sous forme de tensor
        torch.save(embeddings, save_path)
        print(f"Embeddings sauvegardés dans {save_path}.")
    
    return embeddings



def compute_similarity(user_embedding, perfume_embeddings):
    """
    Calcule la similarité cosinus entre un embedding utilisateur et les embeddings des parfums.
    """
    if isinstance(perfume_embeddings, torch.Tensor):
        return cosine_similarity(user_embedding, perfume_embeddings)
    elif isinstance(perfume_embeddings, np.ndarray):
        perfume_embeddings = torch.tensor(perfume_embeddings)
        return cosine_similarity(user_embedding, perfume_embeddings)
    else:
        raise ValueError("Les embeddings des parfums ne sont ni un tensor PyTorch ni un tableau NumPy.")

def get_top_recommendations(similarities, df, top_k=5):
    """
    Récupère les meilleures correspondances en fonction des similarités cosinus.
    """
    # Convertir les similarités en NumPy pour utiliser argsort
    similarities_np = similarities.numpy() if isinstance(similarities, torch.Tensor) else similarities
    top_indices = np.argsort(similarities_np)[::-1][:top_k]
    return df.iloc[top_indices]

def prepare_user_input(description, notes=None, desc_weight=1, notes_weight=2):
    """
    Prépare l'entrée utilisateur en combinant description et notes avec pondération.
    """
    weighted_description = (description + " ") * desc_weight
    if notes:
        weighted_notes = ("Notes: " + notes + ", ") * notes_weight
        return weighted_description + weighted_notes
    return weighted_description

def recommend_perfume(file_path, user_description, notes=None, top_k=5, notes_weight=2, desc_weight=1, save_path="embeddings.pt"):
    """
    Recommande des parfums en fonction des entrées utilisateur (description et notes).
    Retourne les recommandations sous forme de DataFrame pour l'affichage dans Streamlit.
    """
    df = load_and_prepare_data(file_path)
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    perfume_embeddings = load_or_compute_embeddings(df, model, save_path)
    user_input_combined = prepare_user_input(user_description, notes, desc_weight, notes_weight)
    user_embedding = model.encode([user_input_combined], convert_to_tensor=True)
    similarities = compute_similarity(user_embedding, perfume_embeddings)
    recommendations = get_top_recommendations(similarities, df, top_k)
    
    # Créer un DataFrame pour retourner les recommandations à Streamlit
    recommendations_list = []
    for _, row in recommendations.iterrows():
        recommendations_list.append({
            "Parfum": row['Perfume'],
            "Description": row['Description'],
            "Notes": f"{row['Top Notes']} | {row['Middle Notes']} | {row['Base Notes']}",
            "Main Accords": row['Main Accords']
        })

    # Retourner un DataFrame des recommandations pour l'affichage
    return pd.DataFrame(recommendations_list)
