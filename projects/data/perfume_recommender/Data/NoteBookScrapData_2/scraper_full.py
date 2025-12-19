import os
import time
import random
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configurer le driver Selenium
def configure_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# Gérer les cookies
def handle_cookies(driver):
    try:
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//iframe[@title='SP Consent Message']"))
        )
        driver.switch_to.frame(iframe)
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@title='Accept']"))
        )
        accept_button.click()
        driver.switch_to.default_content()
        print("Consentement aux cookies accepté.")
    except Exception as e:
        print(f"Erreur lors de la gestion des cookies : {e}")

# Simuler un comportement humain
def simulate_human_behavior(driver):
    delay = random.uniform(0.5, 1.5)
    print(f"Pause simulant un comportement humain : {delay:.2f} secondes")
    time.sleep(delay)
    driver.execute_script("window.scrollBy(0, 300);")

# Extraire les accords principaux
def extract_main_accords(driver):
    try:
        accord_elements = driver.find_elements(By.XPATH, "//div[@class='cell accord-box']/div[@class='accord-bar']")
        main_accords = [accord.text.strip() for accord in accord_elements if accord.text.strip()]
        return ", ".join(main_accords) if main_accords else "Non disponible"
    except Exception as e:
        print(f"Erreur lors de l'extraction des accords principaux : {e}")
        return "Non disponible"

# Extraire les notes depuis la description
def parse_notes_from_description(description):
    try:
        top_notes = re.search(r"Top notes? (?:are|is) (.*?)(;|\\.|,|$)", description, re.IGNORECASE)
        middle_notes = re.search(r"middle notes? (?:are|is) (.*?)(;|\\.|,|$)", description, re.IGNORECASE)
        base_notes = re.search(r"base notes? (?:are|is) (.*?)(;|\\.|,|$)", description, re.IGNORECASE)

        return (
            top_notes.group(1).strip() if top_notes else "Non disponible",
            middle_notes.group(1).strip() if middle_notes else "Non disponible",
            base_notes.group(1).strip() if base_notes else "Non disponible",
        )
    except Exception as e:
        print(f"Erreur lors de l'extraction des notes : {e}")
        return "Non disponible", "Non disponible", "Non disponible"

# Vérifier si le site a bloqué l'accès
def is_blocked(driver):
    try:
        if "429" in driver.page_source or "Too Many Requests" in driver.title:
            print("Bloqué : 429 Too Many Requests")
            return True
        return False
    except Exception:
        return False

# Extraire les données d'un parfum
def extract_data(link, index):
    driver = configure_driver()
    try:
        driver.get(link)
        handle_cookies(driver)
        simulate_human_behavior(driver)

        perfume = driver.find_element(By.XPATH, "//h1").text.strip() if driver.find_elements(By.XPATH, "//h1") else "Non disponible"
        brand = driver.find_element(By.XPATH, "//p[contains(text(), 'by')]/b[2]").text.strip() if driver.find_elements(By.XPATH, "//p[contains(text(), 'by')]/b[2]") else "Non disponible"

        description = driver.find_element(By.XPATH, "//div[@class='cell small-12' and @itemprop='description']").text.strip() if driver.find_elements(By.XPATH, "//div[@class='cell small-12' and @itemprop='description']") else "Non disponible"
        top_notes, middle_notes, base_notes = parse_notes_from_description(description)

        rating = driver.find_element(By.XPATH, "//span[@itemprop='ratingValue']").text.strip() if driver.find_elements(By.XPATH, "//span[@itemprop='ratingValue']") else "Non disponible"
        rating_count = driver.find_element(By.XPATH, "//span[@itemprop='ratingCount']").text.strip() if driver.find_elements(By.XPATH, "//span[@itemprop='ratingCount']") else "Non disponible"

        main_accords = extract_main_accords(driver)

        return {
            "URL": link,
            "Perfume": perfume,
            "Brand": brand,
            "Description": description,
            "Top Notes": top_notes,
            "Middle Notes": middle_notes,
            "Base Notes": base_notes,
            "Rating": rating,
            "Rating Count": rating_count,
            "Main Accords": main_accords,
        }
    except Exception as e:
        print(f"Erreur pour {link} : {e}")
        return None
    finally:
        driver.quit()

# Scraping complet à partir des liens
def scrape_complete_perfume_data(input_file, output_file, max_links_per_hour=50, pause_duration=1900):
    data = pd.read_excel(input_file)
    links = data["Perfume URL"]  # Vérifiez que cette colonne est correctement nommée
    results = []
    processed_links = set()
    

    for i, link in enumerate(links):
        if link in processed_links:
            print(f"Lien déjà traité : {link}")
            continue

        print(f"Traitement du lien {i + 1}/{len(links)} : {link}")
        data = extract_data(link, i)
        if data:
            results.append(data)
            processed_links.add(link)

        if (i + 1) % max_links_per_hour == 0 or i + 1 == len(links):
            df = pd.DataFrame(results)
            df.to_excel(output_file, index=False)
            print(f"Données sauvegardées dans {output_file}.")

        if (i + 1) % max_links_per_hour == 0:
            print(f"Pause de {pause_duration // 60} minutes pour éviter les blocages.")
            time.sleep(pause_duration)
