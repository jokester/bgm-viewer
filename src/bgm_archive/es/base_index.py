from pydantic import BaseModel
from elasticsearch import AsyncElasticsearch
from typing import Iterable, AsyncIterable
from elasticsearch.helpers import async_streaming_bulk
from typing import TypeVar, Generic
import logging

ModelType = TypeVar("ModelType", bound=BaseModel)

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


class BaseIndex(Generic[ModelType]):
    def __init__(self, es: AsyncElasticsearch, index_name: str, model_type: ModelType):
        self.__es = es
        self.__index_name = index_name
        self.__model_type = model_type

    async def get_by_id(self, id: int) -> ModelType | None:
        response = await self.__es.search(index=self.__index_name, query={"term": {"id": id}})
        print(response)
        hits = response.get('hits', {}).get('hits', [])
        if len(hits) == 0:
            return None
        elif len(hits) == 1:
            return self.__model_type.model_validate(hits[0]['_source'])
        else:
            logger.warning(
                f"Multiple hits found for id {id} in index {self.__index_name} - len(hits)={len(hits)}")
            return None

    async def recreate_index(self):
        await self.__es.indices.delete(index=self.__index_name, ignore_unavailable=True)
        # print("mappings", self.es_mappings)
        await self.__es.indices.create(
            index=self.__index_name,
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
                    yield {"_index": self.__index_name, **doc.model_dump(mode="json")}
        elif isinstance(documents, Iterable):

            def producer():
                for doc in documents:
                    # print(f"Indexing document: {doc}")
                    yield {"_index": self.__index_name, **doc.model_dump(mode="json")}
        else:
            raise TypeError("documents must be Iterable or AsyncIterable")

        async for succeed, details in async_streaming_bulk(
            client=self.__es,
            actions=producer(),
            max_retries=10,
            # raise_on_error=False,
        ):
            if not succeed:
                print(f"Failed to index document: {details}")

    @property
    def es_mappings(self) -> dict:
        raise NotImplementedError(
            "Subclasses must implement the mappings property")
