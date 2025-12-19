import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
from matplotlib.colors import LinearSegmentedColormap

# Configuration de la page Streamlit
st.set_page_config(page_title="Analyse des Parfums", layout="wide")
st.title("Analyse Interactive des Données de Parfums")

# Section : Chargement des données
st.sidebar.header("Télécharger les données")
uploaded_file = st.sidebar.file_uploader("Importer un fichier Excel", type=["xlsx"])

if uploaded_file:
    # Charger les données
    df = pd.read_excel(uploaded_file)

    # Vérification et nettoyage des données
    if 'Rating' in df.columns:
        df['Rating'] = pd.to_numeric(df['Rating'].astype(str).str.replace(',', '.'), errors='coerce')
    else:
        st.error("Le fichier doit contenir une colonne 'Rating'.")

    st.sidebar.success("Fichier chargé avec succès !")

    # Section : Aperçu des données
    st.header("Aperçu des données")
    st.dataframe(df.head())

    # Section : Statistiques descriptives
    st.header("Statistiques descriptives")
    st.write(df.describe(include='all'))

    # Graphique 1 : Distribution des ratings
    st.subheader("Distribution des Ratings des Parfums")
    fig, ax = plt.subplots()
    sns.histplot(df['Rating'], kde=True, bins=20, color='#1f77b4', ax=ax)
    ax.set_title("Distribution des Ratings", color='white')
    ax.set_xlabel("Rating", color='white')
    ax.set_ylabel("Nombre de Parfums", color='white')
    ax.tick_params(colors='white')
    plt.style.use('dark_background')
    st.pyplot(fig)

    # Graphique 2 : Répartition par genre
    if 'Gender' in df.columns:
        st.subheader("Répartition des Parfums par Genre")
        fig, ax = plt.subplots()
        sns.countplot(data=df, x='Gender', palette='pastel', ax=ax)
        ax.set_title("Répartition des Parfums par Genre")
        ax.set_xlabel("Genre")
        ax.set_ylabel("Nombre de Parfums")
        st.pyplot(fig)

        # Graphique 3 : Boxplot des ratings par genre
        st.subheader("Ratings par Genre")
        fig, ax = plt.subplots()
        sns.boxplot(data=df, x='Gender', y='Rating', palette='coolwarm', ax=ax)
        ax.set_title("Ratings par Genre")
        ax.set_xlabel("Genre")
        ax.set_ylabel("Rating")
        st.pyplot(fig)
    else:
        st.warning("La colonne 'Gender' est absente du fichier. Certains graphiques ne peuvent pas être générés.")

    # Nouveau graphique : Scatterplot sans les labels en abscisse
    # Définir une palette personnalisée
    df['Rating Count'] = pd.to_numeric(df['Rating Count'], errors='coerce')
    palette = {
    'Men': 'blue',
    'Women': 'purple',
    'Unisex': 'green',
    'Unknown': 'gray'  
    }

    # Nouveau graphique : Scatterplot sans les labels en abscisse
    st.subheader("Popularité vs Rating")
    fig, ax = plt.subplots()
    sns.scatterplot(data=df, x='Rating Count', y='Rating', hue='Gender', palette=palette, ax=ax)

    # Personnaliser le titre et les axes
    ax.set_title("Popularité vs Rating")
    ax.set_xlabel("Nombre d'Évaluations")
    ax.set_ylabel("Rating")
    ax.set_xlim(0, df['Rating Count'].max() * 1.1)  

    # Supprimer les ticks en abscisse
    ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)

    # Afficher le graphique dans Streamlit
    st.pyplot(fig)

    # Nuage de mots : Notes Olfactives
    st.subheader("Nuage de Mots : Notes Olfactives")
    df['Top Notes'] = df['Top Notes'].astype(str).fillna('')
    df['Middle Notes'] = df['Middle Notes'].astype(str).fillna('')
    df['Base Notes'] = df['Base Notes'].astype(str).fillna('')
    all_notes = ' '.join(df['Top Notes'] + ' ' + df['Middle Notes'] + ' ' + df['Base Notes'])
    all_notes = all_notes.replace('Non', '').replace('Disponible', '').replace('and', '').replace('disponible','').replace('notes','')
    note_counts = Counter(all_notes.split())

    # Créer le nuage de mots
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(note_counts)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title("Nuage de mots : Notes Olfactives")
    st.pyplot(fig)

    # Graphique des accords les plus récurrents
    st.subheader("Les Accords les plus Récurrents")
    all_accords = ' '.join(df['Main Accords'].fillna('')).split(', ')
    accord_counts = Counter(all_accords)
    most_common_accords = pd.DataFrame(accord_counts.most_common(10), columns=['Accord', 'Count'])

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=most_common_accords, x='Count', y='Accord', palette='muted', ax=ax)
    ax.set_title("Les Accords les plus récurrents")
    ax.set_xlabel("Nombre d'Apparitions")
    ax.set_ylabel("Accords")
    st.pyplot(fig)

    # Analyser les marques
    st.subheader("Analyse par Marque")
    df['Rating Count'] = pd.to_numeric(df['Rating Count'].astype(str).str.replace(',', ''), errors='coerce')

    brand_perfume_count = df['Brand'].value_counts().reset_index()
    brand_perfume_count.columns = ['Brand', 'Perfume Count']

    brand_avg_rating = df.groupby('Brand')['Rating'].mean().reset_index()
    brand_avg_rating.columns = ['Brand', 'Average Rating']

    brand_popularity = df.groupby('Brand')['Rating Count'].sum().reset_index()
    brand_popularity.columns = ['Brand', 'Total Rating Count']

    brand_analysis = brand_perfume_count.merge(brand_avg_rating, on='Brand')
    brand_analysis = brand_analysis.merge(brand_popularity, on='Brand')

    brand_analysis_sorted_by_perfume_count = brand_analysis.sort_values(by='Perfume Count', ascending=False).head(10)
    brand_analysis_sorted_by_rating = brand_analysis.sort_values(by='Average Rating', ascending=False).head(10)

    # Visualisation : Marques dominantes par nombre de parfums
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=brand_analysis_sorted_by_perfume_count, x='Perfume Count', y='Brand', palette='muted', ax=ax)
    ax.set_title("Top 10 des marques par nombre de parfums")
    ax.set_xlabel("Nombre de parfums")
    ax.set_ylabel("Marques")
    st.pyplot(fig)

    # Visualisation : Marques les mieux notées
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=brand_analysis_sorted_by_rating, x='Average Rating', y='Brand', palette='muted', ax=ax)
    ax.set_title("Top 10 des marques les mieux notées")
    ax.set_xlabel("Note moyenne")
    ax.set_ylabel("Marques")
    st.pyplot(fig)

else:
    st.warning("Veuillez télécharger un fichier Excel pour commencer l'analyse.")