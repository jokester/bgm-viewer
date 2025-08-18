from .conn import DuckDbRef
import pandas as pd
import bgm_archive.loader.model as m
from pathlib import Path
from typing import Union


def subject_row_to_model(row: pd.Series | dict) -> m.Subject:
    """Convert a DuckDB table row to a Subject model.

    The DuckDB table stores some fields differently than the model expects:
    - favorite fields are stored as separate columns (favorite_wish, favorite_done, etc.)
    - tags, score_details, and meta_tags are not stored in DuckDB
    """
    # Extract favorite fields and create Favorite object
    favorite = m.Favorite(
        wish=row.get("favorite_wish", 0),
        done=row.get("favorite_done", 0),
        doing=row.get("favorite_doing", 0),
        on_hold=row.get("favorite_on_hold", 0),
        dropped=row.get("favorite_dropped", 0),
    )

    # Create Subject model with available fields
    # Note: tags, score_details, and meta_tags are not available in DuckDB
    subject_dict = {
        "id": row["id"],
        "type": m.SubjectType(row["type"]),
        "name": row["name"],
        "name_cn": row["name_cn"],
        "infobox": row["infobox"],
        "platform": row["platform"],
        "summary": row["summary"],
        "nsfw": row["nsfw"],
        "tags": [],  # Not stored in DuckDB
        "score": row["score"],
        "score_details": None,  # Not stored in DuckDB
        "rank": row["rank"],
        "date": row["date"],
        "favorite": favorite,
        "series": row["series"],
        "meta_tags": None,  # Not stored in DuckDB
    }

    return m.Subject.model_validate(subject_dict)


def character_row_to_model(row: pd.Series | dict) -> m.Character:
    """Convert a DuckDB table row to a Character model."""
    return m.Character.model_validate(
        {
            "id": row["id"],
            "name": row["name"],
            "infobox": row["infobox"],
            "summary": row["summary"],
            "comments": row["comments"],
            "collects": row["collects"],
        }
    )


def person_row_to_model(row: pd.Series | dict) -> m.Person:
    """Convert a DuckDB table row to a Person model."""
    return m.Person.model_validate(
        {
            "id": row["id"],
            "name": row["name"],
            "type": m.PersonType(row["type"]),
            "career": row["career"],
            "infobox": row["infobox"],
            "summary": row["summary"],
            "comments": row["comments"],
            "collects": row["collects"],
        }
    )


def episode_row_to_model(row: pd.Series | dict) -> m.Episode:
    """Convert a DuckDB table row to an Episode model."""
    return m.Episode.model_validate(
        {
            "id": row["id"],
            "name": row["name"],
            "name_cn": row["name_cn"],
            "description": row["description"],
            "airdate": row["airdate"],
            "disc": row["disc"],
            "duration": row["duration"],
            "subject_id": row["subject_id"],
            "sort": row["sort"],
            "type": m.EpisodeType(row["type"]),
        }
    )


class RdbRepository:
    def __init__(self, db: Union[DuckDbRef, str, Path]):
        self._db_ref = DuckDbRef.from_db(db)

    def find_subject_by_id(self, subject_id: int) -> m.Subject | None:
        with self._db_ref.open_db(read_only=False) as conn:
            rows = conn.execute(
                "SELECT * FROM Subjects WHERE id = ?", (subject_id,)
            ).df()
            if not len(rows):
                return None
            return subject_row_to_model(rows.iloc[0])

    def find_character_by_id(self, character_id: int) -> m.Character | None:
        with self._db_ref.open_db(read_only=False) as conn:
            rows = conn.execute(
                "SELECT * FROM Characters WHERE id = ?", (character_id,)
            ).df()
            if not len(rows):
                return None
            return character_row_to_model(rows.iloc[0])

    def find_person_by_id(self, person_id: int) -> m.Person | None:
        with self._db_ref.open_db(read_only=False) as conn:
            rows = conn.execute("SELECT * FROM Persons WHERE id = ?", (person_id,)).df()
            if not len(rows):
                return None
            return person_row_to_model(rows.iloc[0])

    def find_episodes_by_subject_id(self, subject_id: int) -> list[m.Episode]:
        with self._db_ref.open_db(read_only=False) as conn:
            rows = conn.execute(
                "SELECT * FROM Episodes WHERE subject_id = ? ORDER BY sort",
                (subject_id,),
            ).df()
            return [episode_row_to_model(row) for _, row in rows.iterrows()]

    def find_subjects_by_ids(self, subject_ids: list[int]) -> list[m.Subject]:
        if not subject_ids:
            return []
        with self._db_ref.open_db(read_only=False) as conn:
            rows = conn.execute(
                "SELECT * FROM Subjects WHERE id IN ?", (subject_ids,)
            ).df()
            return [subject_row_to_model(row) for _, row in rows.iterrows()]

    def find_characters_by_ids(self, character_ids: list[int]) -> list[m.Character]:
        if not character_ids:
            return []
        with self._db_ref.open_db(read_only=False) as conn:
            rows = conn.execute(
                "SELECT * FROM Characters WHERE id IN ?", (character_ids,)
            ).df()
            return [character_row_to_model(row) for _, row in rows.iterrows()]

    def find_people_by_ids(self, person_ids: list[int]) -> list[m.Person]:
        if not person_ids:
            return []
        with self._db_ref.open_db(read_only=False) as conn:
            rows = conn.execute(
                "SELECT * FROM Persons WHERE id IN ?", (person_ids,)
            ).df()
            return [person_row_to_model(row) for _, row in rows.iterrows()]
