from scraper_full import scrape_complete_perfume_data

def test_scrape_single_designer():
    """
    Test le scraping des parfums pour une marque spécifique (Louis Vuitton).
    Les résultats seront sauvegardés dans un fichier de test spécifique.
    """
    input_file = "test_louis_vuitton_links.xlsx"  # Fichier contenant les liens des parfums Louis Vuitton
    output_file = "test_louis_vuitton_perfume_data.xlsx"  # Fichier de sortie
    scrape_complete_perfu
