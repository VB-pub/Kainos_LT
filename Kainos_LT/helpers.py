from models import Element
from typing import List
from decimal import Decimal

import json, uuid, os

class Data2Json:

    @staticmethod
    def convert(objs: List[Element]) -> str:
        def serialize_element(element):
            # Convert special types to serializable forms
            if isinstance(element, uuid.UUID):
                return str(element)
            if isinstance(element, Decimal):
                return float(element)
            if isinstance(element, Element):
                # Initialize an empty dictionary for the Element
                result = {}

                # Conditionally add each field only if it has meaningful data
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
                # Convert lists recursively
                return [serialize_element(sub_element) for sub_element in element]
            
            return element  # For all other types, return as is

        # Convert each object in the list
        serialized_objs = [serialize_element(obj) for obj in objs]
        
        # Return as a JSON string
        return json.dumps(serialized_objs, indent=4)

    
    @staticmethod
    def save_to_disk(json: str) -> None:
        filename = 'data.json'
        project_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(project_path, filename)

        with open(file_path, 'w') as file:
            file.write(json)