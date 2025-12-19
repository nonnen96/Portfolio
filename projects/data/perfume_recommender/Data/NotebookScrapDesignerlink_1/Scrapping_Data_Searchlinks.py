
## Ce fichier rassemble une autre manière de scrap des données grâce à la page recherche de Fragrantica, cependant il se limite seulement à 1000 liens alors qu'avec la méthode "Designer" on peut scrapper >20k parfums.


import chromedriver_autoinstaller
chromedriver_autoinstaller.install()

from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time 

########################################## ACCEPTER LES COOKIES#########################################################
# Configurer les options de Chrome
options = Options()
options.add_argument("--headless")  # Mode sans interface graphique
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36")

# Configurer le service ChromeDriver
service = Service(ChromeDriverManager().install())

# Lancer le navigateur
driver = webdriver.Chrome(service=service, options=options)

# URL de la page de recherche
base_url = "https://www.fragrantica.com/search/"
driver.get(base_url)
time.sleep(5)  # Attendre que la page se charge

# Capture après ouverture de la page
driver.save_screenshot("screenshots/step_0_initial_page.png")
print("Capture d'écran initiale enregistrée : screenshots/step_0_initial_page.png")

# Étape 1 : Basculer dans l'iframe contenant le message de consentement
try:
    iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//iframe[@title='SP Consent Message']"))
    )
    driver.switch_to.frame(iframe)
    print("Bascule dans l'iframe réussie.")

    # Étape 2 : Cliquer sur le bouton "Accepter"
    accept_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@title='Accept']"))
    )
    accept_button.click()
    print("Consentement aux cookies accepté.")

    # Revenir au contenu principal
    driver.switch_to.default_content()
except Exception as e:
    print(f"Erreur lors de la gestion des cookies : {e}")

# Étape 3 : Capture finale après traitement
driver.save_screenshot("final_state.png")
print("Capture d'écran finale enregistrée : final_state.png") 

########################## VOIR PLUS DE RESULTAT###################

def click_voir_plus_de_resultats():
    try:
        # Rechercher le bouton "Voir plus de résultats"
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Show more results')]"))
        )
        
        # Masquer les publicités bloquantes si présentes
        try:
            ad_iframe = driver.find_element(By.XPATH, "//iframe[contains(@id, 'google_ads_iframe')]")
            driver.execute_script("arguments[0].style.display = 'none';", ad_iframe)
            print("Publicité masquée.")
        except Exception:
            print("Aucune publicité détectée ou déjà masquée.")

        # S'assurer que le bouton est visible en scrollant vers lui
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        time.sleep(2)  # Pause pour permettre le chargement visuel

        # Cliquer sur le bouton en utilisant JavaScript pour contourner les blocages
        driver.execute_script("arguments[0].click();", button)
        print("Clic sur 'Show more results' réussi.")
        time.sleep(1)  # Attendre que les nouveaux résultats se chargent
        return True
    except Exception as e:
        print(f"Le bouton 'Voir plus de résultats' n'est plus disponible ou une erreur est survenue : {e}")
        return False

# Cliquer sur le bouton jusqu'à ce qu'il n'existe plus ou un certain nombre de clics
max_clicks = 50 # Limiter à 100 clics
for i in range(max_clicks):
    print(f"Essai de clic n°{i + 1} sur 'Voir plus de résultats'")
    if not click_voir_plus_de_resultats():
        break

# Capture finale après avoir terminé les clics
driver.save_screenshot("screenshots/final_state2.png")
print("Capture d'écran finale enregistrée : screenshots/final_state2.png")



######## Extraction des liens########

import pandas as pd
# Trouver tous les éléments contenant des liens de parfums
parfum_elements = driver.find_elements(By.XPATH, "//div[@class='cell card fr-news-box']//a")

# Extraire les liens des parfums
parfum_links = []
for parfum in parfum_elements:
    link = parfum.get_attribute("href")
    if link:
        parfum_links.append(link)

# Supprimer les doublons (si plusieurs liens identiques sont collectés)
parfum_links = list(set(parfum_links))

# Sauvegarder les liens dans un fichier Excel
df = pd.DataFrame(parfum_links, columns=["URL"])
df.to_excel("parfum_links.xlsx", index=False)
print(f"Fichier 'parfum_links.xlsx' sauvegardé avec {len(parfum_links)} liens.")

# Fermer le navigateur
driver.quit()

print(df)
