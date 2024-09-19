
import json
from typing import List, Dict, Any
from langchain.schema import Document



# **DataLoader** class to load and process data
class DataLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_data(self) -> List[List[Dict[str, Any]]]:
        with open(self.file_path, "r", encoding='utf-8') as file:
            data = json.load(file)
        return data

    def data_to_documents(self, data: Dict[str, List[Dict[str, str]]]) -> List[Document]:
        documents = []
        for item in data:
            offset = item.get('offset')
            text = item.get('text')
            lang = item.get('lang')
            item_type = item.get('type')
            item_ref = item.get('ref')
            metadata = {
                'type': item_type,
                'ref': item_ref,
                'offset': offset,
                'lang': lang
            }
            doc = Document(page_content=text, metadata=metadata)
            documents.append(doc)
        return documents
