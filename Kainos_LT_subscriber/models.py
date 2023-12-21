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
        
    def __init__(self, type : ElementType, name: str, url : str) -> None:
        self.Id = uuid.uuid5()
        self.Type = type
        self.Name = name
        self.Url = url
        
        Logger.log_init(self)


class Item(Element):
    def __init__(self, name: str, url : str, price : Decimal, currency : str) -> None:
        super().__init__(ElementType.ITEM, name, url)
        self.Price = price
        self.Currency = currency
        
class Category(Element):
    
    items = []
    
    def __init__(self, name: str, url : str, quantity: int) -> None:
        super().__init__(ElementType.CATEGORY, name, url)
        self.Quantity = quantity
        self.Items = []
    
    @classmethod
    def item_add(cls, item : Item) -> None:
        cls.Items.append(item)
        
class Shop(Element):
    
    categories = []
    items = []
    
    def __init__(self, name: str, url: str) -> None:
        super().__init__(ElementType.SHOP, name, url)
    
    @classmethod
    def categories_add(cls, self, category : Category) -> None:
        cls.categories.append(category)
        Logger.log_relationship(self, category)
    
    @classmethod
    def items_add(cls, self, item : Item) -> None:
        cls.items.append(item)
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