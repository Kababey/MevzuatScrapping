import os
import time
import requests
import urllib3
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

#  SSL uyarılarını kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#  PDF’lerin indirileceği klasör
DOWNLOAD_DIR = "cbk_pdfs"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

#  Tarayıcı ayarları
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 15)

BASE_URL = "####################" # Buraya gerekli url yi girin
BASE_DOMAIN = "#################" # Buraya gerekli domaini girin
TOTAL_PAGES = 4

# 1️ Sayfaya git ve Ara butonuna bas
print(" Sayfa açılıyor...")
driver.get(BASE_URL)
#wait.until(EC.element_to_be_clickable((By.ID, "btnSearch"))).click()

driver.execute_script('document.querySelectorAll("#btnSearch")[2].click()')

time.sleep(2)

# 2️ Tüm sayfaları gez
for sayfa_index in range(1, TOTAL_PAGES + 1):
    print(f"\n Sayfa {sayfa_index} işleniyor...")

    try:
        if sayfa_index > 1:
            try:
                pagination_links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.pagination li a.page-link")))
                clicked = False
                for link in pagination_links:
                    if link.text.strip() == str(sayfa_index):
                        driver.execute_script("arguments[0].click();", link)
                        time.sleep(3)
                        clicked = True
                        break
                if not clicked:
                    print(f" Sayfa {sayfa_index} görünür değil, geçilemedi.")
                    break
            except Exception as e:
                print(f" Sayfa {sayfa_index} geçiş hatası: {e}")
                break

        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#DataTables_Table_0 tbody tr")))
        satirlar = driver.find_elements(By.CSS_SELECTOR, "#DataTables_Table_0 tbody tr")
        print(f" {len(satirlar)} mevzuat bulundu.")

        for i in range(len(satirlar)):
            try:
                satirlar = driver.find_elements(By.CSS_SELECTOR, "#DataTables_Table_0 tbody tr")
                link = satirlar[i].find_element(By.CSS_SELECTOR, "td a").get_attribute("href")
                full_link = urljoin(BASE_DOMAIN, link)

                print(f"\n {i+1}. mevzuat detay linki: {full_link}")
                driver.execute_script("window.open(arguments[0], '_blank');", full_link)
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(2)

                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, "//a[img[contains(@src, 'iconPdf')]]")))
                    pdf_link = driver.find_element(By.XPATH, "//a[img[contains(@src, 'iconPdf')]]").get_attribute("href")

                    file_name = pdf_link.split("/")[-1]
                    file_path = os.path.join(DOWNLOAD_DIR, file_name)

                    if os.path.exists(file_path):
                        print(f" Zaten var: {file_name}")
                    else:
                        print(f" PDF indiriliyor: {pdf_link}")
                        headers = {
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                        }
                        response = requests.get(pdf_link, headers=headers, verify=False)
                        if response.status_code == 200:
                            with open(file_path, "wb") as f:
                                f.write(response.content)
                            print(f" Kaydedildi: {file_name}")
                        else:
                            print(f" HTTP {response.status_code} hatası: {pdf_link}")

                except Exception as e:
                    print(f" PDF bulunamadı: {e}")

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            except Exception as e:
                print(f" Satır hatası: {e}")

    except Exception as e:
        print(f" Sayfa {sayfa_index} yüklenemedi: {e}")
        break

driver.quit()
print("\n Tüm işlemler tamamlandı.")