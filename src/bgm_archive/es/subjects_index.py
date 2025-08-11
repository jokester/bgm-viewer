from pydantic import BaseModel
from .base_index import BaseIndex


class SubjectsIndexQuery(BaseModel):
    pass


class SubjectsIndex(BaseIndex):
    @property
    def es_mappings(self) -> dict:
        return {
            'properties': {
                'id': {
                    'type': 'long'
                },
                'type': {
                    'type': 'integer'
                },
                'name': {
                    'type': 'text',
                    'analyzer': 'mixed_cjk_english',
                },
                'name_cn': {
                    'type': 'text',
                    'analyzer': 'mixed_cjk_english',
                },
                'infobox': {
                    'type': 'text',
                    'analyzer': 'mixed_cjk_english',
                },
                'platform': {
                    'type': 'integer'
                },
                'summary': {
                    'type': 'text',
                    'analyzer': 'mixed_cjk_english',
                },
                'nsfw': {
                    'type': 'boolean'
                },
                'tags': {
                    'type': 'nested',
                    'properties': {
                        'name': {
                            'type': 'text',
                            'analyzer': 'mixed_cjk_english',
                        },
                        'count': {
                            'type': 'integer'
                        }
                    }
                },
                'score': {
                    'type': 'float'
                },
                'score_details': {
                    'type': 'object',
                    'properties': {
                        'score_1': {'type': 'integer'},
                        'score_2': {'type': 'integer'},
                        'score_3': {'type': 'integer'},
                        'score_4': {'type': 'integer'},
                        'score_5': {'type': 'integer'},
                        'score_6': {'type': 'integer'},
                        'score_7': {'type': 'integer'},
                        'score_8': {'type': 'integer'},
                        'score_9': {'type': 'integer'},
                        'score_10': {'type': 'integer'}
                    }
                },
                'rank': {
                    'type': 'integer'
                },
                'date': {
                    'type': 'date'
                },
                'favorite': {
                    'type': 'object',
                    'properties': {
                        'wish': {'type': 'integer'},
                        'done': {'type': 'integer'},
                        'doing': {'type': 'integer'},
                        'on_hold': {'type': 'integer'},
                        'dropped': {'type': 'integer'}
                    }
                },
                'series': {
                    'type': 'boolean'
                },
                'meta_tags': {
                    'type': 'keyword'
                }
            }
        }
