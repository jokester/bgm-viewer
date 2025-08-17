from .base_index import BaseIndex
from bgm_archive.loader import model


class EpisodeIndex(BaseIndex):
    def __init__(self, es, index_name: str):
        super().__init__(es, index_name, model.Episode)

    @property
    def es_mappings(self) -> dict:
        return {
            "properties": {
                "id": {"type": "long"},
                "name": {"type": "text", "analyzer": "mixed_cjk_english"},
                "name_cn": {"type": "text", "analyzer": "mixed_cjk_english"},
                "description": {"type": "text", "analyzer": "mixed_cjk_english"},
                # "airdate": {"type": "date"},
                # not date: this field has too many malformed dates
                "airdate": {"type": "text"},
                "disc": {"type": "integer"},
                "duration": {"type": "text"},
                "subject_id": {"type": "long"},
                "sort": {"type": "float"},
                "type": {"type": "integer"},
            }
        }
