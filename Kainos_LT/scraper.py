#external
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException

#internal
from typing import List
from threading import Thread

import re, threading, uuid, time

#local
from logger import Logger
from models import Category, Item, Shop
from exceptions import CategoryNoUrlError
from concurency import ItemWorker, Worker

class Scraper:
                
    def __init__(self, item_page_concurency = 1, max_concurency = 5, headless=True):
        self.base_url = 'https://www.kainos.lt/'
        self.item_page_concurency = item_page_concurency
        self.max_concurency = max_concurency
        self.shut_down = False
        self.threads = []
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
            self.options.add_argument("--window-size=1920,1080")
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
            self.options.add_argument(f'user-agent={user_agent}')
        self.driver = webdriver.Chrome(options=self.options)

    def run(self, time_limit=60):
        self.load_page()
        self.cookie_trust_handle()
        root_categories = self.get_category_root()

        def timer_thread(time_limit):
            time.sleep(time_limit)
            self.cancel()
            print(f"Time limit of {time_limit} seconds reached. Signalling cancellation...")

        timer = Thread(target=timer_thread, args=(time_limit,))
        timer.start()

        for cat in root_categories:
            if self.shut_down:
                break
            self.try_get_category_recursive(cat)

        while sum(1 for t in self.threads if t is not None) > 0:
            time.sleep(1)

        timer.join()
            
    def cancel(self):
        Worker.cancel_all()
        self.shut_down = True
        self.close()

    def load_page(self):
        self.driver.get(self.base_url)

    def close(self):
        self.driver.quit()

    def get_category_elements(self, parent : Category) -> []:
        try:
            
            if self.shut_down:
                return None
            
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
            
            if self.shut_down:
                return None
            
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
                obj = self.create_shop_obj(shop)
                if obj is None:
                    continue
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
                
        gaqPush_element = shop.find_element(By.CLASS_NAME, 'title-container').find_element(By.TAG_NAME, 'a').get_attribute('onClick')
        
        if not gaqPush_element:
            return None
        
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
            
            if self.shut_down:
                return False
            
            if not parent:
                return False
            
            if not parent.Url:
                raise CategoryNoUrlError(f"Category {parent.Name} doesn't have url!")
            
            self.driver.get(parent.Url)
                        
            categories = self.get_category_elements(parent)
            
            if not categories:
                if self.item_page_concurency == 1:
                    self.get_page_items_root(parent)
                elif self.item_page_concurency > 1:
                    self.get_page_items_concurent(parent)
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
        
    def get_page_items_concurent(self, category : Category) -> List[Item]:
        try:
            if self.shut_down:
                return None
            
            correlation_id = uuid.uuid4()          
            for i in range(1, self.item_page_concurency):
                scraper = Scraper()
                item_worker = ItemWorker(correlation_id)
                jobs = [
                    lambda: scraper.driver.get(category.Url + f'?page={item_worker.current_page}'),
                    lambda: [scraper.get_shops(item) for item in scraper.get_item_elements(category) if not self.shut_down],
                    lambda: scraper.driver.get(category.Url + f'?page={item_worker.current_page}')
                ]
                self.threads.append(threading.Thread(target=item_worker.run, args=(jobs, scraper.try_get_item_paginator, scraper.close)).start())
                        
        except BaseException as ex:
            Logger.log_error(category, ex)
            return None
        
    def get_page_items_root(self, category : Category) -> List[Item]:
        try:
            if self.shut_down:
                return None      
            
            self.driver.get(category.Url)
            paginatorNext = self.try_get_item_paginator()
            
            items = self.get_item_elements(category)
            
            for item in items:
                if self.shut_down:
                    return None
                self.get_shops(item)
            
            
            self.try_get_page_items_recursive(category, paginatorNext)
            
        except BaseException as ex:
            Logger.log_error(category, ex)
            return None
        
    def try_get_page_items_recursive(self, category : Category, paginatorNext: str) -> bool:
        try:
            if self.shut_down:
                return False
            
            if not paginatorNext:
                raise CategoryNoUrlError(f"Category {category.Name} doesn't have next page!")
        
            self.driver.get(paginatorNext)
            paginatorNext = self.try_get_item_paginator()
            result = self.get_item_elements(category)
        
            if not result:
                return False
        
            for item in result:
                if self.shut_down:
                    return False
                self.get_shops(item)
        
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