from .base_index import BaseIndex
from bgm_archive.loader import model


class PersonIndex(BaseIndex):
    def __init__(self, es, index_name: str):
        super().__init__(es, index_name, model.Person)

    @property
    def es_mappings(self) -> dict:
        return {
            "properties": {
                "id": {"type": "long"},
                "name": {"type": "text", "analyzer": "mixed_cjk_english"},
                "type": {"type": "integer"},
                "career": {"type": "keyword"},
                "infobox": {"type": "text", "analyzer": "mixed_cjk_english"},
                "summary": {"type": "text", "analyzer": "mixed_cjk_english"},
                "comments": {"type": "integer"},
                "collects": {"type": "integer"},
            }
        }
