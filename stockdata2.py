import os
import time
from selenium import webdriver

file_name = "riskdata.csv"
file_path = os.path.join(os.getcwd(), file_name)

if os.path.exists(file_path):
    os.remove(file_path)
    print(f"{file_name} has been deleted.")
else:
    print(f"{file_name} does not exist.")
    
options = webdriver.ChromeOptions()
preferences = {
    "download.default_directory": os.getcwd(),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", preferences)
#options.add_argument("--headless")

driver = webdriver.Chrome(chrome_options=options)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://investors.sgx.com/stock-screener"
driver.get(url)

# Wait for the download button to be clickable
options_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/main/div[1]/article/template-tools-page/section/widget-stock-screener/div/sgx-table/sgx-table-toolbar/div[1]/widget-stock-screener-toolbar/div/button")))
options_button.click()
customise_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/sgx-dialog[1]/div[2]/div/a[2]")))
customise_button.click()
yrRevChange_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/sgx-dialog[7]/div[2]/sgx-select-picker/sgx-list/div/div/sgx-select-picker-option[19]/label/span[2]")))
yrRevChange_button.click()
update_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/sgx-dialog[7]/div[2]/footer/button[1]")))
update_button.click()
options_button.click()
download_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/sgx-dialog[1]/div[2]/div/a[1]")))
download_button.click()
time.sleep(2)
driver.close()

for file in os.listdir(os.getcwd()):
    if file.startswith("SGX Screener Data"):
        random_file_name = file
        break
        
# rename the downloaded file
os.rename(os.path.join(os.getcwd(), random_file_name), os.path.join(os.getcwd(), "riskdata.csv"))

