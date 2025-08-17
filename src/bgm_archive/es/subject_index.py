from pydantic import BaseModel
from typing import Optional, List
import logging
from .base_index import BaseIndex, SearchResult
from bgm_archive.loader import model

logger = logging.getLogger(__name__)


class SubjectsIndexQuery(BaseModel):
    query: str
    limit: int = 20
    offset: int = 0
    type: Optional[int] = None
    subject_type: Optional[int] = None  # Alias for type field
    nsfw: Optional[bool] = None


class SubjectSearchResult(SearchResult[model.Subject]):
    """Result model for subject search operations."""
    pass


class SubjectsIndex(BaseIndex[model.Subject]):
    def __init__(self, es, index_name: str):
        super().__init__(es, index_name, model.Subject)

    async def search(self, search_query: SubjectsIndexQuery) -> SubjectSearchResult:
        """Search subjects using Elasticsearch."""
        query_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": search_query.query,
                                "fields": [
                                    "name^3",
                                    "name_cn^3",
                                    "summary^2",
                                    "infobox^1",
                                    "tags.name^2",
                                ],
                                "type": "best_fields",
                                "fuzziness": "AUTO",
                            }
                        }
                    ],
                    "filter": [],
                }
            },
            "size": search_query.limit,
            "from": search_query.offset,
            "sort": [
                {"_score": {"order": "desc"}},
                {"score": {"order": "desc"}},
                {"rank": {"order": "asc"}},
            ],
        }

        # Add filters if specified
        if search_query.type is not None:
            query_body["query"]["bool"]["filter"].append(
                {"term": {"type": search_query.type}}
            )
        
        # Handle subject_type alias for type field
        if search_query.subject_type is not None:
            query_body["query"]["bool"]["filter"].append(
                {"term": {"type": search_query.subject_type}}
            )
            
        # Add NSFW filter if specified
        if search_query.nsfw is not None:
            query_body["query"]["bool"]["filter"].append(
                {"term": {"nsfw": search_query.nsfw}}
            )

        response = await self._es.search(index=self._index_name, body=query_body)

        hits = response.get("hits", {}).get("hits", [])
        total = response.get("hits", {}).get("total", {}).get("value", 0)
        
        subjects = []
        for hit in hits:
            try:
                subject = self._model_type.model_validate(hit["_source"])
                subjects.append(subject)
            except Exception as e:
                logger.warning(f"Failed to parse subject from search result: {e}")
                continue

        has_more = (search_query.offset + search_query.limit) < total
        
        return SubjectSearchResult(
            items=subjects,
            total=total,
            query=search_query.query,
            limit=search_query.limit,
            offset=search_query.offset,
            has_more=has_more
        )

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
