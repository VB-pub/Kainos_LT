from enum import Enum
from decimal import Decimal
from abc import ABC

import uuid
import traceback

class ElementType(Enum):
    NONE = 0
    CATEGORY = 1
    ITEM = 2
    SHOP = 3

class Element(ABC):
    
    shops = []
    categories = []
    items = []
        
    def __init__(self, type : ElementType, name: str, url : str) -> None:
        self.Id = uuid.uuid5()
        self.Type = type
        self.Name = name
        self.Url = url
        
        if type is ElementType.SHOP:
            Element.shops.append(self)
        elif type is ElementType.CATEGORY:
            Element.categories.append(self)
        elif type is ElementType.ITEM:
            Element.items.append(self)
        
        Logger.log_init(self)


class Item(Element):
    def __init__(self, name: str, url : str, price : Decimal, currency : str) -> None:
        super().__init__(ElementType.ITEM, name, url)
        self.Price = price
        self.Currency = currency
        
class Category(Element):
        
    def __init__(self, name: str, url : str, quantity: int) -> None:
        super().__init__(ElementType.CATEGORY, name, url)
        self.Quantity = quantity
        self.Items = []
    
    def item_add(self, item : Item) -> None:
        self.Items.append(item)
        Logger.log_relationship(self, item)
        
class Shop(Element):
        
    def __init__(self, name: str, url: str) -> None:
        super().__init__(ElementType.SHOP, name, url)
        self.Items = []
        self.Categories = []
        
    def categories_add(self, category : Category) -> None:
        self.Categories.append(category)
        Logger.log_relationship(self, category)
    
    def items_add(self, item : Item) -> None:
        self.Items.append(item)
        Logger.log_relationship(self, item)
        
class Logger:
    
    @staticmethod
    def log_relationship(entity1 : Element, entity2 : Element) -> None:
        print(f'{entity1.Name} pridėtas į {entity2.Name}')
        
    @staticmethod
    def log_init(entity : Element) -> None:  
        print(f'{entity.Id} sukurtas elementas {entity.Type}: {entity.Name}')
        
    @staticmethod
    def log_error(entity : Element, ex : Exception) -> None:  
        formatted_traceback = ''.join(traceback.format_exception(None, ex, ex.__traceback__))
        print(f'ERROR: {entity.Name} {entity.Type}: {formatted_traceback}')