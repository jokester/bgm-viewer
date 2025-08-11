from elasticsearch import AsyncElasticsearch
from typing import Iterable, AsyncIterable
from elasticsearch.helpers import async_streaming_bulk


from pydantic import BaseModel


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


class BaseIndex:
    def __init__(self, es: AsyncElasticsearch, index_name: str):
        self.__es = es
        self.__index_name = index_name

    async def recreate_index(self):
        await self.__es.indices.delete(index=self.__index_name, ignore_unavailable=True)
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
