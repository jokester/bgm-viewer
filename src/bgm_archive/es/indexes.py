from pydantic import BaseModel
from .base_index import BaseIndex
from bgm_archive.loader import model


class SubjectsIndexQuery(BaseModel):
    pass


class SubjectsIndex(BaseIndex):
    def __init__(self, es, index_name: str):
        super().__init__(es, index_name, model.Subject)

    @property
    def es_mappings(self) -> dict:
        return {
            "properties": {
                "id": {"type": "long"},
                "type": {"type": "integer"},
                "name": {
                    "type": "text",
                    "analyzer": "mixed_cjk_english",
                },
                "name_cn": {
                    "type": "text",
                    "analyzer": "mixed_cjk_english",
                },
                "infobox": {
                    "type": "text",
                    "analyzer": "mixed_cjk_english",
                },
                "platform": {"type": "integer"},
                "summary": {
                    "type": "text",
                    "analyzer": "mixed_cjk_english",
                },
                "nsfw": {"type": "boolean"},
                "tags": {
                    "type": "nested",
                    "properties": {
                        "name": {
                            "type": "text",
                            "analyzer": "mixed_cjk_english",
                        },
                        "count": {"type": "integer"},
                    },
                },
                "score": {"type": "float"},
                "score_details": {
                    "type": "object",
                    "properties": {
                        "score_1": {"type": "integer"},
                        "score_2": {"type": "integer"},
                        "score_3": {"type": "integer"},
                        "score_4": {"type": "integer"},
                        "score_5": {"type": "integer"},
                        "score_6": {"type": "integer"},
                        "score_7": {"type": "integer"},
                        "score_8": {"type": "integer"},
                        "score_9": {"type": "integer"},
                        "score_10": {"type": "integer"},
                    },
                },
                "rank": {"type": "integer"},
                "date": {"type": "date"},
                "favorite": {
                    "type": "object",
                    "properties": {
                        "wish": {"type": "integer"},
                        "done": {"type": "integer"},
                        "doing": {"type": "integer"},
                        "on_hold": {"type": "integer"},
                        "dropped": {"type": "integer"},
                    },
                },
                "series": {"type": "boolean"},
                "meta_tags": {"type": "keyword"},
            }
        }


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


class CharacterIndex(BaseIndex):
    def __init__(self, es, index_name: str):
        super().__init__(es, index_name, model.Character)

    @property
    def es_mappings(self) -> dict:
        return {
            "properties": {
                "id": {"type": "long"},
                "role": {"type": "integer"},
                "name": {"type": "text", "analyzer": "mixed_cjk_english"},
                "infobox": {"type": "text", "analyzer": "mixed_cjk_english"},
                "summary": {"type": "text", "analyzer": "mixed_cjk_english"},
                "comments": {"type": "integer"},
                "collects": {"type": "integer"},
            }
        }


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
