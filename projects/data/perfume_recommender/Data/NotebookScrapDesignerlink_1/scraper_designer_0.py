import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configurer le driver
def configure_driver():
    options = Options()
    options.add_argument("--headless")  # Mode sans interface graphique
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def prepare_scraping():
    driver = configure_driver()
    base_url = "https://www.fragrantica.com/designers/"
    driver.get(base_url)
    time.sleep(5)

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
    except Exception as e:
        print(f"Erreur lors de la gestion des cookies : {e}")
    return driver


def scrape_designer_links(driver, output_file="designer_links.xlsx"):
    designer_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/designers/')]")
    designer_links = [element.get_attribute("href").split(".com")[-1] for element in designer_elements if element.get_attribute("href")]
    pd.DataFrame(designer_links, columns=["Relative URL"]).to_excel(output_file, index=False)
    print(f"{len(designer_links)} liens de marques collectés et sauvegardés dans '{output_file}'.")


def scrape_single_designer(designer_url, output_file="single_designer_perfume_links.xlsx"):
    full_url = f"https://www.fragrantica.com{designer_url}"
    driver = configure_driver()
    driver.get(full_url)
    time.sleep(3)

    perfume_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/perfume/')]")
    perfume_links = [element.get_attribute("href") for element in perfume_elements]
    perfume_links = list(set(perfume_links))  # Supprimer les doublons

    pd.DataFrame(perfume_links, columns=["Perfume URL"]).to_excel(output_file, index=False)
    print(f"{len(perfume_links)} liens de parfums collectés pour {designer_url} et sauvegardés dans '{output_file}'.")
    driver.quit()




# Fonction générale pour tous les parfums :

import time
import pandas as pd
from selenium.webdriver.common.by import By

import time
import pandas as pd
from selenium.webdriver.common.by import By

def scrape_all_designers(input_file="designer_links.xlsx", output_file="all_designers_perfume_links.xlsx", max_requests=50, pause_duration=1800):
    """
    Scraper les liens de parfums pour toutes les marques listées dans le fichier `input_file`, 
    avec une limite de 50 requêtes toutes les 30 minutes.

    :param input_file: Fichier Excel contenant les liens relatifs des marques (par défaut `designer_links.xlsx`).
    :param output_file: Fichier Excel pour sauvegarder les liens des parfums (par défaut `all_designers_perfume_links.xlsx`).
    :param max_requests: Nombre maximum de requêtes à effectuer avant une pause (par défaut 50).
    :param pause_duration: Durée de la pause en secondes après chaque batch de requêtes (par défaut 1800s = 30 minutes).
    """
    # Charger le fichier contenant les liens des marques
    designer_data = pd.read_excel(input_file)
    designer_links = designer_data["Relative URL"].tolist()

    all_perfume_links = []  # Liste pour stocker tous les liens de parfums
    print(f"Nombre de marques à traiter : {len(designer_links)}")

    # Traiter les marques par lot pour respecter les limites
    for batch_start in range(0, len(designer_links), max_requests):
        batch_end = min(batch_start + max_requests, len(designer_links))
        batch_links = designer_links[batch_start:batch_end]
        print(f"Traitement du batch {batch_start + 1} à {batch_end}...")

        for i, designer_link in enumerate(batch_links, start=batch_start + 1):
            full_url = f"https://www.fragrantica.com{designer_link}"
            print(f"  [{i}/{len(designer_links)}] Scraping des parfums pour la marque : {full_url}")

            driver = configure_driver()  # Configurer un nouveau driver pour chaque marque
            try:
                driver.get(full_url)
                time.sleep(3)  # Attendre que la page se charge

                # Scraper les liens des parfums
                perfume_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/perfume/')]")
                perfume_links = [element.get_attribute("href") for element in perfume_elements]
                print(f"    > {len(perfume_links)} parfums trouvés.")

                all_perfume_links.extend(perfume_links)  # Ajouter à la liste globale
            except Exception as e:
                print(f"Erreur lors du scraping pour {designer_link} : {e}")
            finally:
                driver.quit()  # Fermer le driver pour éviter des conflits

        # Supprimer les doublons à chaque batch
        all_perfume_links = list(set(all_perfume_links))

        # Sauvegarde incrémentale après chaque batch
        pd.DataFrame(all_perfume_links, columns=["Perfume URL"]).to_excel(output_file, index=False)
        print(f"Batch terminé. Sauvegarde intermédiaire dans '{output_file}'.")
        
        # Pause après avoir atteint la limite de requêtes
        if batch_end < len(designer_links):  # Éviter la pause après le dernier batch
            print(f"Pause de {pause_duration // 60} minutes pour respecter les limites.")
            time.sleep(pause_duration)

    print(f"Scraping terminé : {len(all_perfume_links)} liens de parfums collectés et sauvegardés dans '{output_file}'.")



