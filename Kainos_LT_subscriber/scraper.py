from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException

from logger import Logger
from models import Category, Item, Shop
from exceptions import CategoryNoUrlError

import re

class Scraper:
                
    def __init__(self, headless=True):
        self.base_url = 'https://www.kainos.lt/'
        self.options = Options()
        if headless:
            self.options.add_argument('--headless=new')
        self.driver = webdriver.Chrome()

    def load_page(self):
        self.driver.get(self.base_url)

    def close(self):
        self.driver.quit()

    def get_category_elements(self) -> []:
        try:
            WebDriverWait(self.driver, timeout=1).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'title_categories'))
            )
            
            elements = self.driver.find_element(By.CLASS_NAME, 'title_categories').find_elements(By.CLASS_NAME, 'tile')
            
            objs = []
            for element in elements:
                objs.append(self.create_category_obj(element))
            
            return objs
        except TimeoutException:
            Logger.log_error(f'{self.driver.current_url}:Has no categories!')
            return None
                        

    def create_category_obj(self, category : WebElement) -> Category:
        name_n_count = category.find_element(By.CLASS_NAME, 'category_title').text.splitlines()

        if len(name_n_count) == 1:
            name_n_count.append("0")

        url = category.find_element(By.CLASS_NAME, 'title_category').get_attribute('href')
        return Category(name_n_count[0], url, int(re.sub(r"[^\d]", "", name_n_count[1])))

    def get_category_root(self) -> []:
        try:      
            
            categories = self.get_category_elements()
                  
            if not categories:
                raise RuntimeError("No categories found!")
          
            return categories
        except BaseException as ex:
            Logger.log_error(None, ex)
            return None
            

    def try_get_category_recursive(self, parent : Category) -> bool:
        try:
            if not parent:
                return False
            
            if not parent.Url:
                raise CategoryNoUrlError(f"Category {parent.Name} doesn't have url!")
            
            self.driver.get(parent.Url)
            
            categories = self.get_category_elements()
            
            if not categories:
                return False
            
            for category in categories:
                self.try_get_category_recursive(category)
            
        except CategoryNoUrlError as ex:
            Logger.log_error(None, ex)
            return False
        except BaseException as ex:
            Logger.log_error(parent, ex)
            return False
        
    def get_page_items(self, category : Category) -> []:
        self.driver.get(category.Url)
        
        WebDriverWait(self.driver, timeout=1).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'results'))
        )

        item_list = self.driver.find_element(By.ID, 'results').find_elements(By.CLASS_NAME, 'product-tile-inner')

        for item in item_list:
            name = item.find_element(By.CLASS_NAME, 'title')
            url = item.find_element(By.TAG_NAME, 'a').get_attribute('href')
            price = 1
            Item(name, url, price)

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