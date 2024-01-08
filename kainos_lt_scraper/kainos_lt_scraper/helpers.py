from .models import Element
from typing import List, Union, Any, Optional
from decimal import Decimal

import json
import uuid
import os

class Data2Json:
    """A utility class for converting complex objects to JSON and saving them to disk."""

    @staticmethod
    def convert(objs: List[Element]) -> str:
        """
        Convert a list of Element objects (or other supported types) to a JSON string.
        
        :param objs: A list of Element objects to be converted.
        :return: A JSON string representation of the list.
        """
        def serialize_element(element: Any) -> Union[dict, list, str, float, None]:
            """Recursively serialize an element to a JSON-compatible format."""
            if isinstance(element, uuid.UUID):
                return str(element)
            if isinstance(element, Decimal):
                return float(element)
            if isinstance(element, Element):
                result: dict = {}

                if element.Id is not None:
                    result['Id'] = serialize_element(element.Id)
                if element.Type is not None:
                    result['Type'] = element.Type.name
                if element.Name:
                    result['Name'] = element.Name
                if element.Url:
                    result['Url'] = element.Url
                if hasattr(element, 'Price') and element.Price is not None:
                    result['Price'] = serialize_element(element.Price)
                if hasattr(element, 'Shops') and element.Shops:
                    result['Shops'] = serialize_element(element.Shops)
                if hasattr(element, 'Quantity') and element.Quantity is not None:
                    result['Quantity'] = serialize_element(element.Quantity)
                if hasattr(element, 'SubCategories') and element.SubCategories:
                    result['SubCategories'] = serialize_element(element.SubCategories)
                if hasattr(element, 'Items') and element.Items:
                    result['Items'] = serialize_element(element.Items)

                return result

            if isinstance(element, list):
                return [serialize_element(sub_element) for sub_element in element]

            return element

        serialized_objs: List[dict] = [serialize_element(obj) for obj in objs]
        
        return json.dumps(serialized_objs, indent=4)

    
    @staticmethod
    def save_to_disk(json_str: str) -> None:
        """
        Save a JSON string to a file in the project's directory.
        
        :param json_str: The JSON string to be saved.
        """
        filename: str = 'data.json'
        project_path: str = os.path.dirname(os.path.abspath(__file__))
        file_path: str = os.path.join(project_path, filename)

        with open(file_path, 'w') as file:
            file.write(json_str)
