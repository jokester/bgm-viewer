import os
from typing import Callable
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import dotenv
import concurrent.futures as cf

from bgm_archive.duck import RdbRepository, GraphEdge, Subgraph, GraphRepository
from bgm_archive.es import (
    SubjectsIndex,
    SubjectsIndexQuery,
    SubjectSearchResult,
    CharactersIndexQuery,
    CharacterSearchResult,
    PersonsIndexQuery,
    PersonSearchResult,
    EpisodesIndexQuery,
    EpisodeSearchResult,
    get_async_client,
    CharacterIndex,
    PersonIndex,
    EpisodeIndex,
)
import bgm_archive.loader.model as m
import asyncio

dotenv.load_dotenv()

rdb = RdbRepository(db=os.environ["DUCKDB_PATH"])
gdb = GraphRepository(db=os.environ["DUCKDB_PATH"], rdb=rdb)

thread_pool = cf.ThreadPoolExecutor(
    max_workers=int(os.environ.get("THREAD_POOL_SIZE", 10))
)


def in_thread(foo: Callable) -> asyncio.Future:
    return asyncio.wrap_future(thread_pool.submit(foo))


def parse_ids(ids_param: str | None) -> list[int]:
    if ids_param is None or ids_param.strip() == "":
        return []
    parts = [p.strip() for p in ids_param.split(",") if p.strip() != ""]
    ids: list[int] = []
    for part in parts:
        if not part.isdigit():
            raise HTTPException(status_code=400, detail=f"Invalid id: {part}")
        ids.append(int(part))
    return ids


def build_app() -> FastAPI:
    fastapi = FastAPI()

    # Add CORS middleware to allow any CORS requests
    fastapi.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
    )

    es_client = get_async_client()
    subjects_index = SubjectsIndex(es_client, "bgm_subjects")
    person_index = PersonIndex(es_client, "bgm_persons")
    char_index = CharacterIndex(es_client, "bgm_characters")
    episode_index = EpisodeIndex(es_client, "bgm_episodes")

    @fastapi.post("/subjects/search", response_model=SubjectSearchResult)
    async def search_subjects(search_query: SubjectsIndexQuery):
        """Search subjects using Elasticsearch."""
        try:
            results = await subjects_index.search(search_query)
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    @fastapi.post("/characters/search", response_model=CharacterSearchResult)
    async def search_characters(search_query: CharactersIndexQuery):
        """Search characters using Elasticsearch."""
        try:
            results = await char_index.search(search_query)
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    @fastapi.post("/people/search", response_model=PersonSearchResult)
    async def search_people(search_query: PersonsIndexQuery):
        """Search people using Elasticsearch."""
        try:
            results = await person_index.search(search_query)
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    @fastapi.post("/episodes/search", response_model=EpisodeSearchResult)
    async def search_episodes(search_query: EpisodesIndexQuery):
        """Search episodes using Elasticsearch."""
        try:
            results = await episode_index.search(search_query)
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    @fastapi.get("/subjects/{subject_id}", response_model=m.Subject)
    def get_subject(subject_id: int):
        subject = rdb.find_subject_by_id(subject_id)
        if subject is None:
            raise HTTPException(status_code=404, detail="Subject not found")
        return subject

    @fastapi.get("/subjects/multiple", response_model=list[m.Subject])
    def get_subjects_multiple(ids: str | None = Query(default=None)):
        subject_ids = parse_ids(ids)
        return rdb.find_subjects_by_ids(subject_ids)

    @fastapi.get("/subjects/{subject_id}/episodes", response_model=list[m.Episode])
    def get_subject_episodes(subject_id: int):
        return rdb.find_episodes_by_subject_id(subject_id)

    @fastapi.get("/subjects/{subject_id}/edges", response_model=Subgraph)
    async def get_subject_edges(subject_id: int):
        subject = rdb.find_subject_by_id(subject_id)
        if subject is None:
            raise HTTPException(status_code=404, detail="Subject not found")
        s2s_edges, s2c_edges, s2p_edges = await asyncio.gather(
            in_thread(lambda: gdb.expand_s2s(subject)),
            in_thread(lambda: gdb.expand_s2c(subject)),
            in_thread(lambda: gdb.expand_s2p(subject)),
        )
        return Subgraph(from_subject=subject, edges=s2s_edges + s2c_edges + s2p_edges)

    @fastapi.get("/characters/{character_id}", response_model=m.Character)
    def get_character(character_id: int):
        character = rdb.find_character_by_id(character_id)
        if character is None:
            raise HTTPException(status_code=404, detail="Character not found")
        return character

    @fastapi.get("/characters/multiple", response_model=list[m.Character])
    def get_characters_multiple(ids: str | None = Query(default=None)):
        character_ids = parse_ids(ids)
        return rdb.find_characters_by_ids(character_ids)

    @fastapi.get("/characters/{character_id}/edges", response_model=Subgraph)
    async def get_character_edges(character_id: int):
        character = rdb.find_character_by_id(character_id)
        if character is None:
            raise HTTPException(status_code=404, detail="Character not found")
        c2s_edges, c2p_edges = await asyncio.gather(
            in_thread(lambda: gdb.expand_cs(character)),
            in_thread(lambda: gdb.expand_c2p(character)),
        )
        return Subgraph(from_character=character, edges=c2p_edges)

    @fastapi.get("/people/{person_id}", response_model=m.Person)
    def get_person(person_id: int):
        person = rdb.find_person_by_id(person_id)
        if person is None:
            raise HTTPException(status_code=404, detail="Person not found")
        return person

    @fastapi.get("/people/multiple", response_model=list[m.Person])
    def get_people_multiple(ids: str | None = Query(default=None)):
        person_ids = parse_ids(ids)
        return rdb.find_people_by_ids(person_ids)

    @fastapi.get("/people/{person_id}/edges", response_model=Subgraph)
    async def get_person_edges(person_id: int):
        person = rdb.find_person_by_id(person_id)
        if person is None:
            raise HTTPException(status_code=404, detail="Person not found")
        p2s_edges, p2c_edges = await asyncio.gather(
            in_thread(lambda: gdb.expand_p2s(person)),
            in_thread(lambda: gdb.expand_p2c(person)),
        )
        return Subgraph(from_person=person, edges=p2s_edges + p2c_edges)

    return fastapi


app = build_app()
__all__ = ["app"]
