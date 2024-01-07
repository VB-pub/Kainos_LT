from enum import Enum
from decimal import Decimal
from abc import ABC
from typing import List, Type
from logger import Logger
import uuid

class ExportType(Enum):
    JSON = 0
    CONSOLE = 0

class ElementType(Enum):
    NONE = 0
    CATEGORY = 1
    ITEM = 2
    SHOP = 3

class Element(ABC):
    categories: List['Category'] = []
    items: List['Item'] = []

    def __init__(self, type: ElementType, name: str, url: str) -> None:
        self.Id: uuid.UUID = uuid.uuid4()
        self.Type: ElementType = type
        self.Name: str = name
        self.Url: str = url

        if type == ElementType.CATEGORY:
            Element.categories.append(self)
        elif type == ElementType.ITEM:
            Element.items.append(self)

        Logger.log_init(self)

class Shop(Element):
    def __init__(self, name: str, url: str, price: Decimal) -> None:
        super().__init__(ElementType.SHOP, name, url)
        self.Price: Decimal = price

class Item(Element):
    def __init__(self, name: str, url: str) -> None:
        super().__init__(ElementType.ITEM, name, url)
        self.Shops: List[Shop] = []

    def add_shop(self, shop: Shop) -> None:
        self.Shops.append(shop)
        Logger.log_relationship(self, shop)

class Category(Element):
    def __init__(self, name: str, url: str, quantity: int) -> None:
        super().__init__(ElementType.CATEGORY, name, url)
        self.Quantity: int = quantity
        self.SubCategories: List['Category'] = []
        self.Items: List[Item] = []

    def item_add(self, item: Item) -> None:
        self.Items.append(item)
        Logger.log_relationship(self, item)

    def sub_category_add(self, category: 'Category') -> None:
        self.SubCategories.append(category)
        Logger.log_relationship(self, category)
