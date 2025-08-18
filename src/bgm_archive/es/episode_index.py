from pydantic import BaseModel
from typing import Optional, List
import logging
from .base_index import BaseIndex, SearchResult
from bgm_archive.loader import model

logger = logging.getLogger(__name__)


class EpisodesIndexQuery(BaseModel):
    query: str
    limit: int = 20
    offset: int = 0
    type: Optional[int] = None
    subject_id: Optional[int] = None


class EpisodeSearchResult(SearchResult[model.Episode]):
    """Result model for episode search operations."""

    pass


class EpisodeIndex(BaseIndex[model.Episode]):
    def __init__(self, es, index_name: str):
        super().__init__(es, index_name, model.Episode)

    async def search(self, search_query: EpisodesIndexQuery) -> EpisodeSearchResult:
        """Search episodes using Elasticsearch."""
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
                                    "description^2",
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
                {"sort": {"order": "asc"}},
            ],
        }

        # Add filters if specified
        if search_query.type is not None:
            query_body["query"]["bool"]["filter"].append(
                {"term": {"type": search_query.type}}
            )

        if search_query.subject_id is not None:
            query_body["query"]["bool"]["filter"].append(
                {"term": {"subject_id": search_query.subject_id}}
            )

        response = await self._es.search(index=self._index_name, body=query_body)

        hits = response.get("hits", {}).get("hits", [])
        total = response.get("hits", {}).get("total", {}).get("value", 0)

        episodes = []
        for hit in hits:
            try:
                episode = self._model_type.model_validate(hit["_source"])
                episodes.append(episode)
            except Exception as e:
                logger.warning(f"Failed to parse episode from search result: {e}")
                continue

        has_more = (search_query.offset + search_query.limit) < total

        return EpisodeSearchResult(
            items=episodes,
            total=total,
            query=search_query.query,
            limit=search_query.limit,
            offset=search_query.offset,
            has_more=has_more,
        )

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
