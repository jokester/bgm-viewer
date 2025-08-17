from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List
from pydantic import BaseModel
from elasticsearch import AsyncElasticsearch
from typing import Iterable, AsyncIterable
from elasticsearch.helpers import async_streaming_bulk
import logging

T = TypeVar('T')

class SearchResult(BaseModel, Generic[T]):
    """Base result model for search operations."""
    items: List[T]
    total: int
    query: str
    limit: int
    offset: int
    has_more: bool

logger = logging.getLogger(__name__)

_analysis = {
    "analysis": {
        "analyzer": {
            "mixed_cjk_english": {
                "type": "custom",
                "tokenizer": "standard",
                "filter": ["lowercase", "cjk_width", "cjk_bigram", "english_stop"],
            }
        },
        "filter": {"english_stop": {"type": "stop", "stopwords": "_english_"}},
    }
}


class BaseIndex(ABC, Generic[T]):
    """Base class for Elasticsearch indexes."""
    
    def __init__(self, es: AsyncElasticsearch, index_name: str, model_type: type[T]):
        self._es = es
        self._index_name = index_name
        self._model_type = model_type

    async def get_by_id(self, id: int) -> T | None:
        response = await self._es.search(
            index=self._index_name, query={"term": {"id": id}}
        )
        print(response)
        hits = response.get("hits", {}).get("hits", [])
        if len(hits) == 0:
            return None
        elif len(hits) == 1:
            return self._model_type.model_validate(hits[0]["_source"])
        else:
            logger.warning(
                f"Multiple hits found for id {id} in index {self._index_name} - len(hits)={len(hits)}"
            )
            return None

    async def recreate_index(self):
        await self._es.indices.delete(index=self._index_name, ignore_unavailable=True)
        # print("mappings", self.es_mappings)
        await self._es.indices.create(
            index=self._index_name,
            body={
                "settings": {**_analysis},
                "mappings": self.es_mappings,
            },
        )

    async def add_documents(
        self, documents: Iterable[BaseModel] | AsyncIterable[BaseModel]
    ):
        if isinstance(documents, AsyncIterable):

            async def producer():  # pyright: ignore[reportRedeclaration]
                async for doc in documents:
                    # print(f"Indexing document: {doc}")
                    yield {"_index": self._index_name, **doc.model_dump(mode="json")}
        elif isinstance(documents, Iterable):

            def producer():
                for doc in documents:
                    # print(f"Indexing document: {doc}")
                    yield {"_index": self._index_name, **doc.model_dump(mode="json")}
        else:
            raise TypeError("documents must be Iterable or AsyncIterable")

        async for succeed, details in async_streaming_bulk(
            client=self._es,
            actions=producer(),
            max_retries=10,
            # raise_on_error=False,
        ):
            if not succeed:
                print(f"Failed to index document: {details}")

    @abstractmethod
    async def search(self, search_query) -> SearchResult[T]:
        """Search using Elasticsearch."""
        pass

    @property
    @abstractmethod
    def es_mappings(self) -> dict:
        """Return Elasticsearch mappings for this index."""
        pass
