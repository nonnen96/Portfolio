
# PerfumeMatch  
Semantic Recommendation of Niche Perfumes from Free-Text Descriptions

---

## Project Overview

PerfumeMatch is a semantic recommendation system that suggests a niche perfume based on a free-text description provided by the user.

The project uses semantic search and sentence embeddings to match user descriptions (moods, atmospheres, olfactory impressions) with existing niche perfumes stored in a curated database. The objective is to offer an intuitive way to discover fragrances aligned with personal preferences or a desired ambiance.

---

## Methodology

The recommendation pipeline relies on:
- Natural Language Processing (NLP)
- Sentence embeddings
- Cosine similarity for semantic matching

User input is embedded into a semantic space and compared with embedded perfume descriptions to retrieve the most relevant recommendations.

---

## Project Structure

The project is structured into three main components, each with dedicated notebooks:

- **Data**: scraping, cleaning, and preprocessing of perfume data  
- **Analysis**: exploratory analysis and feature preparation  
- **Model**: embedding generation and recommendation logic  

---

## Application

Interactive Streamlit applications are available for both the Analysis and Model components.

To run the application:
```bash
streamlit run <filename>.py



