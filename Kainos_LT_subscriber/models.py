from enum import Enum
from decimal import Decimal
from abc import ABC
from logger import Logger

import uuid

class ElementType(Enum):
    NONE = 0
    CATEGORY = 1
    ITEM = 2
    SHOP = 3

class Element(ABC):
    
    categories = []
    items = []
        
    def __init__(self, type : ElementType, name: str, url : str) -> None:
        self.Id = uuid.uuid4()
        self.Type = type
        self.Name = name
        self.Url = url
        
        if type is ElementType.CATEGORY:
            Element.categories.append(self)
        elif type is ElementType.ITEM:
            Element.items.append(self)
        
        Logger.log_init(self)

class Shop(Element):
        
    def __init__(self, name: str, url: str, price : Decimal) -> None:
        super().__init__(ElementType.SHOP, name, url)
        self.Price = price

class Item(Element):
    def __init__(self, name: str, url : str) -> None:
        super().__init__(ElementType.ITEM, name, url)
        self.Shops = []
        
    def add_shop(self, shop : Shop):
        self.Shops.append(shop)
        Logger.log_relationship(self, shop)
        
        
class Category(Element):
        
    def __init__(self, name: str, url : str, quantity: int) -> None:
        super().__init__(ElementType.CATEGORY, name, url)
        self.Quantity = quantity
        self.SubCategories = []
        self.Items = []
    
    def item_add(self, item : Item) -> None:
        self.Items.append(item)
        Logger.log_relationship(self, item)

    def sub_category_add(self, category : 'Category') -> None:
        self.SubCategories.append(category)
        Logger.log_relationship(self, category)
        
    