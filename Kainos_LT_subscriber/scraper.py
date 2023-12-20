from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

class Scraper:
    
    categories = []
    
    def __init__(self, headless=True):
        self.options = Options()
        if headless:
            self.options.add_argument('--headless=new')
        self.driver = webdriver.Chrome()

    def load_page(self):
        self.driver.get('https://www.kainos.lt/')

    def close(self):
        self.driver.quit()

    def item_search(self, q : str):
        try:
            search_id = 'search_form'
            
            WebDriverWait(self.driver, timeout=5).until(
                EC.presence_of_element_located((By.ID, search_id))
            )
            
            search_element = self.driver.find_element(By.ID, search_id)
            input_element = search_element.find_element(By.NAME, 'q')
            submit_element = search_element.find_element(By.ID, 'header_search_button')
            
            input_element.clear()
            input_element.send_keys(q)
            submit_element.click()
        except:
            print('err')
        
    def cookie_trust_handle(self):
        try:
            WebDriverWait(self.driver, timeout=10).until(
                EC.presence_of_element_located((By.ID, "onetrust-button-group"))
            )
    
            cookie_trust_element = self.driver.find_element(By.ID, "onetrust-button-group")
            cookie_trust_reject_element = cookie_trust_element.find_element(By.ID, "onetrust-reject-all-handler")
            cookie_trust_reject_element.click()
        except:
            print("No cookie trust element.")
    
    def categories_load(self):
        try:
            category_list_class_toggle = 'category-filter-toggle'

            WebDriverWait(self.driver, timeout=5).until(
                EC.presence_of_element_located((By.XPATH, f"//a[contains(@class, '{category_list_class_toggle}')]"))
            )

            category_list_toggle_element = self.driver.find_element(By.XPATH, f"//a[contains(@class, '{category_list_class_toggle}')]")
            category_list_toggle_element.click()

            category_list_loaded = "loaded"

            WebDriverWait(self.driver, timeout=5).until(
                EC.presence_of_element_located((By.XPATH, f"//ul[contains(@class, '{category_list_loaded}')]"))
            )

            category_list_element = self.driver.find_element(By.XPATH, f"//ul[contains(@class, '{category_list_loaded}')]")
            category_elements = category_list_element.find_elements(By.TAG_NAME, 'a')
            self.categories.clear()
            self.categories = category_elements
        except:
            print('err')
            
    def category_click(self, element : WebElement):
        try:
            element.click()
            self.categories_load()
        except:
            print('err')