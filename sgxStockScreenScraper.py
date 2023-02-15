import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(options=chrome_options)
# from selenium.webdriver.chrome.options import Options
#
# options = Options()
#
# # Set the download directory to a specific directory
# download_directory = os.getcwd()
# options.add_experimental_option("prefs", {
#   "download.default_directory": download_directory,
#   "download.prompt_for_download": False,
#   "download.directory_upgrade": True,
#   "safebrowsing.enabled": True
# })
#
# driver = webdriver.Chrome(options=options)

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://investors.sgx.com/stock-screener"
driver = webdriver.Chrome()
driver.get(url)

# Wait for the download button to be clickable
download_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/main/div[1]/article/template-tools-page/section/widget-stock-screener/div/sgx-table/sgx-table-toolbar/div[1]/widget-stock-screener-toolbar/div/button")))
download_button.click()
download_button2 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/sgx-dialog[1]/div[2]/div/a[1]")))
download_button2.click()

time.sleep(2)
driver.close()