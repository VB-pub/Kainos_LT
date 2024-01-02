from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from logger import Logger
from models import Category, Item, Shop
from exceptions import CategoryNoUrlError
from typing import List

import re
import threading

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

    def get_category_elements(self, parent : Category) -> []:
        try:
            WebDriverWait(self.driver, timeout=1).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'title_categories'))
            )
            
            elements_holder = self.driver.find_elements(By.CLASS_NAME, 'title_categories')[-1:]
            
            if not elements_holder:
                return []
            
            elements = elements_holder[0].find_elements(By.CLASS_NAME, 'tile')
            
            objs = []
            for element in elements[1:]:
                obj = self.create_category_obj(element)
                if parent:
                    parent.sub_category_add(obj)
                objs.append(obj)
            
            return objs
        except TimeoutException:
            Logger.log_warning(f'{self.driver.current_url}:Has no categories!')
            return None
                        

    def get_item_elements(self, category: Category) -> []:
        try:
            
            WebDriverWait(self.driver, timeout=1).until(
                EC.presence_of_element_located((By.ID, 'results'))
            )

            item_list = self.driver.find_element(By.ID, 'results').find_elements(By.CLASS_NAME, 'product-tile-inner')
            
            objs = []
            for item in item_list:
                obj = self.create_item_obj(item)
                if category:
                    category.item_add(obj)
                objs.append(obj)
                
            return objs
                
        except TimeoutException:
            Logger.log_warning(f'{self.driver.current_url}:Page has no items!')
            return None
    
    def get_shop_elements(self, item: Item) -> []:
        try:
            
            WebDriverWait(self.driver, timeout=1).until(
                EC.presence_of_element_located((By.ID, 'prices-container'))
            )

            shop_list = self.driver.find_element(By.ID, 'prices-container').find_elements(By.CLASS_NAME, 'inner')
            
            objs = []
            for shop in shop_list:
                obj = self.create_shop_obj(item)
                if shop:
                    item.add_shop(obj)
                objs.append(obj)
                
            return objs
                
        except TimeoutException:
            Logger.log_warning(f'{self.driver.current_url}:Page has no items!')
            return None
    
    def create_category_obj(self, category : WebElement) -> Category:
        name_n_count = category.find_element(By.CLASS_NAME, 'category_title').text.splitlines()

        if len(name_n_count) == 1:
            name_n_count.append("0")

        url = category.find_element(By.CLASS_NAME, 'title_category').get_attribute('href')
        return Category(name_n_count[0], url, int(re.sub(r"[^\d]", "", name_n_count[1])))

    def create_item_obj(self, item : WebElement) -> Item:
        name = item.find_element(By.CLASS_NAME, 'title').text
        url = item.find_element(By.TAG_NAME, 'a').get_attribute('href')
        return Item(name, url)
        
    def create_shop_obj(self, shop : WebElement) -> Shop:
        
        gaqPush_element = shop.find_element(By.CLASS_NAME, 'title-container').get_attribute('onClick')
        name = re.search(r".*'([^']+)'", gaqPush_element.split(';')[0]).group(1) 
        
        price = shop.find_element(By.CLASS_NAME, 'price-container').text
        url = name
        return Shop(name, url, price)

    def get_category_root(self) -> []:
        try:      
            
            categories = self.get_category_elements(None)
                  
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
                        
            categories = self.get_category_elements(parent)
            
            if not categories:
                self.get_page_items_root(parent)
                return False
            
            for category in categories:
                self.try_get_category_recursive(category)
                
            return True
            
        except CategoryNoUrlError as ex:
            Logger.log_error(None, ex)
            return False
        except BaseException as ex:
            Logger.log_error(parent, ex)
            return False
        
    def get_page_items_root(self, category : Category) -> List[Item]:
        try:
                        
            self.driver.get(category.Url)
        
            items = self.get_item_elements(category)

            for item in items:
                #TODO: separate selenium driver; bugfix
                thread = threading.Thread(target=self.get_shops, args=(item))
                thread.start()
            
            paginatorNext = self.try_get_item_paginator()
            self.try_get_page_items_recursive(category, paginatorNext)
            
        except BaseException as ex:
            Logger.log_error(category, ex)
            return None
        
    def try_get_page_items_recursive(self, category : Category, paginatorNext: str) -> bool:
        try:
            
            if not paginatorNext:
                raise CategoryNoUrlError(f"Category {category.Name} doesn't have next page!")
        
            self.driver.get(paginatorNext)
            result = self.get_item_elements(category)
        
            if not result:
                return False
        
            paginatorNext = self.try_get_item_paginator()
            self.try_get_page_items_recursive(category, paginatorNext)      
                
            return True
        
        except CategoryNoUrlError as ex:
            Logger.log_warning(ex.args[0])
            return False
        except BaseException as ex:
            Logger.log_error(category, ex)
            return False
        
    
    def try_get_item_paginator(self) -> str:
        try:
            return self.driver.find_element(By.XPATH, '//link[contains(@rel, "next")]').get_attribute('href')
        except NoSuchElementException:
            return None
    
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
    
    def get_shops(self, item : Item) -> []:
        try:
                        
            self.driver.get(item.Url)
        
            self.get_shop_elements(item)
            
        except BaseException as ex:
            Logger.log_error(item, ex)
            return None