#external
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException

#internal
from typing import List, Optional
from threading import Thread

import re, threading, uuid, time

#local
from logger import Logger
from models import Category, Item, Shop
from exceptions import CategoryNoUrlError
from concurency import ItemWorker, Worker

class Scraper:
    """A scraper class to navigate and extract data from a kainos.lt using Selenium."""  
    
    def __init__(self, item_page_concurency = 1, max_concurency = 5, headless=True):
        """Initialize the scraper with concurrency settings and headless option."""
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

    def run(self, time_limit=60) -> None:
        """
        Run the scraper for a given time limit.
        
        :param time_limit: The maximum time to run the scraper in seconds.
        """
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
            
    def cancel(self) -> None:
        """Signal the scraper to shut down at the next opportunity."""
        Worker.cancel_all()
        self.shut_down = True
        self.close()

    def load_page(self) -> None:
        """Load the base URL into the web driver."""
        self.driver.get(self.base_url)

    def close(self) -> None:
        """Close the Selenium web driver and all associated windows."""
        self.driver.quit()

    def get_category_elements(self, parent: Optional[Category]) -> Optional[List[Category]]:
        """
        Get category elements from a given parent category.
        
        :param parent: The parent category to search within.
        :return: A list of Category objects or None.
        """
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
                        

    def get_item_elements(self, category: Category) -> Optional[List[Item]]:
        """
        Extract item elements from the specified category's page.
        
        :param category: The category from which to extract items.
        :return: A list of Item objects representing the extracted items.
        """
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
    
    def get_shop_elements(self, item: Item) -> Optional[List[Shop]]:
        """
        Extract shop elements from the specified item's page.
        
        :param item: The item from which to extract associated shops.
        :return: A list of Shop objects representing the extracted shops.
        """
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
    
    def create_category_obj(self, category: WebElement) -> Category:
        """
        Create a Category object from a WebElement representing a category.
        
        :param category: The WebElement representing a category.
        :return: A Category object.
        """
        name_n_count = category.find_element(By.CLASS_NAME, 'category_title').text.splitlines()

        if len(name_n_count) == 1:
            name_n_count.append("0")

        url = category.find_element(By.CLASS_NAME, 'title_category').get_attribute('href')
        return Category(name_n_count[0], url, int(re.sub(r"[^\d]", "", name_n_count[1])))

    def create_item_obj(self, item: WebElement) -> Item:
        """
        Create an Item object from a WebElement representing an item.
        
        :param item: The WebElement representing an item.
        :return: An Item object.
        """
        name = item.find_element(By.CLASS_NAME, 'title').text
        url = item.find_element(By.TAG_NAME, 'a').get_attribute('href')
        return Item(name, url)
        
    def create_shop_obj(self, shop: WebElement) -> Optional[Shop]:
        """
        Create a Shop object from a WebElement representing a shop.
        
        :param shop: The WebElement representing a shop.
        :return: A Shop object or None if the shop couldn't be created.
        """
                
        gaqPush_element = shop.find_element(By.CLASS_NAME, 'title-container').find_element(By.TAG_NAME, 'a').get_attribute('onClick')
        
        if not gaqPush_element:
            return None
        
        name = re.search(r".*'([^']+)'", gaqPush_element.split(';')[0]).group(1) 
        
        price = shop.find_element(By.CLASS_NAME, 'price-container').text
        url = name
        return Shop(name, url, price)

    def get_category_root(self) -> Optional[List[Category]]:
        """
        Get the root categories from the base page.
        
        :return: A list of root Category objects.
        """
        try:      
            
            categories = self.get_category_elements(None)
                  
            if not categories:
                raise RuntimeError("No categories found!")
          
            return categories
        except BaseException as ex:
            Logger.log_error(None, ex)
            return None
            

    def try_get_category_recursive(self, parent: Category) -> bool:
        """
        Attempt to recursively navigate and scrape categories starting from the parent.
        
        :param parent: The parent category from which to begin scraping.
        :return: True if successful, False otherwise.
        """
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
        
    def get_page_items_concurent(self, category: Category) -> Optional[List[Item]]:
        """
        Extract items from the category's page using concurrent threads.
        
        :param category: The category from which to extract items.
        :return: A list of extracted Item objects or None if the operation failed.
        """
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
        
    def get_page_items_root(self, category: Category) -> Optional[List[Item]]:
        """
        Extract items from the category's page without using concurrency.
        
        :param category: The category from which to extract items.
        :return: A list of extracted Item objects or None if the operation failed.
        """
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
        
    def try_get_page_items_recursive(self, category: Category, paginatorNext: str) -> bool:
        """
        Attempt to recursively navigate and scrape items from paginated pages.
        
        :param category: The category for which to scrape paginated items.
        :param paginatorNext: The URL of the next page to scrape.
        :return: True if successful, False otherwise.
        """
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
        
    
    def try_get_item_paginator(self) -> Optional[str]:
        """
        Attempt to find the URL for the next page of items.
        
        :return: The URL of the next page or None if not found.
        """
        try:
            return self.driver.find_element(By.XPATH, '//link[contains(@rel, "next")]').get_attribute('href')
        except NoSuchElementException:
            return None
    
    def cookie_trust_handle(self) -> None:
        """
        Attempt to handle and dismiss the cookie trust (consent) element.
        """
        try:
            WebDriverWait(self.driver, timeout=10).until(
                EC.presence_of_element_located((By.ID, "onetrust-button-group"))
            )
    
            cookie_trust_element = self.driver.find_element(By.ID, "onetrust-button-group")
            cookie_trust_reject_element = cookie_trust_element.find_element(By.ID, "onetrust-reject-all-handler")
            cookie_trust_reject_element.click()
        except:
            print("No cookie trust element.")
    
    def get_shops(self, item: Item) -> Optional[List[Shop]]:
        """
        Navigate to the item's page and extract associated shops.
        
        :param item: The item for which to extract associated shops.
        :return: A list of Shop objects or None if the operation failed.
        """
        try:                  
            self.driver.get(item.Url)
        
            self.get_shop_elements(item)
            
        except BaseException as ex:
            Logger.log_error(item, ex)
            return None