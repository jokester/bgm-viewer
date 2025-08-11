import os
from typing import Optional
from elasticsearch import AsyncElasticsearch, Elasticsearch
import functools
import logging

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1)
def get_async_client() -> AsyncElasticsearch:
    conn_url = os.environ["ES_URL"]
    assert conn_url, "$ES_URL not set"

    client = AsyncElasticsearch(hosts=conn_url)
    return client


async def async_connect() -> AsyncElasticsearch:
    c = get_async_client()
    await c.ping()
    logger.info("Connected to ElasticSearch")
    return c


@functools.lru_cache(maxsize=1)
def sync_connect() -> Elasticsearch:
    conn_url = os.environ["ES_URL"]
    client = Elasticsearch(hosts=conn_url)
    assert client.ping(), "cannot ping ES"
    return client
