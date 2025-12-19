import streamlit as st
import pandas as pd
from perfume_recommender import recommend_perfume

file_path = "/home/onyxia/work/PerfumeMatch/Model/perfume_data_cleaned.xlsx"

save_path = "/home/onyxia/work/PerfumeMatch/Model/embeddings.pt"

# Titre principal
st.title("🌟 PerfumeMatch 🌟")
st.subheader("Découvrez le parfum qui correspond à votre description 💐")

# Champ pour la description du parfum
user_description = st.text_area(
    label="🖊️ Décrivez le type de parfum que vous recherchez",
    placeholder="Exemple : Un parfum frais et floral, idéal pour l'été."
)

# Champ pour les notes préférées
notes = st.text_input(
    label="🎵 Notes préférées (optionnel)",
    placeholder="Exemple : jasmin, vanille, musc"
)

# Paramètres avancés
st.sidebar.header("⚙️ Paramètres avancés")
top_k = st.sidebar.slider("Nombre de recommandations à afficher", min_value=1, max_value=10, value=5)
notes_weight = st.sidebar.slider("Pondération des notes", min_value=1, max_value=5, value=2)
desc_weight = st.sidebar.slider("Pondération de la description", min_value=1, max_value=5, value=1)

# Bouton pour lancer les recommandations
if st.button("🔍 Trouver un parfum"):
    if not user_description.strip():
        st.error("❌ Veuillez entrer une description valide.")
    else:
        st.info("✨ Lancement des recommandations...")
        try:
            recommendations = recommend_perfume(
                file_path=file_path,
                user_description=user_description,
                notes=notes,
                top_k=top_k,
                notes_weight=notes_weight,
                desc_weight=desc_weight,
                save_path=save_path
            )

            if recommendations.empty:
                st.warning("😞 Aucun parfum ne correspond à votre description.")
            else:
                st.success("✅ Recommandations terminées ! Voici vos résultats :")
                for index, row in recommendations.iterrows():
                    st.write(f"### {row['Parfum']} 🌹")
                    st.write(f"**Description :** {row['Description']}")
                    st.write(f"**Notes :** {row['Notes']}")
                    st.write(f"**Main Accords :** {row['Main Accords']}")
                    st.markdown("---")

        except Exception as e:
            st.error(f"⚠️ Une erreur est survenue : {e}")
