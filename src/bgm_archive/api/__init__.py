import os
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Query
import dotenv

from bgm_archive.duck import RdbRepository
import bgm_archive.loader.model as m

dotenv.load_dotenv()

rdb = RdbRepository(db=os.environ["DUCKDB_PATH"])


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

    return fastapi


app = build_app()
__all__ = ["app"]
