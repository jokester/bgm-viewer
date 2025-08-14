import itertools
import json
from pathlib import Path
from typing import Iterator, cast
import logging
import tempfile
import contextlib

from bgm_archive.loader import WikiArchiveLoader, model
from .conn import DuckDbRef

logger = logging.getLogger(__name__)


class DuckdbStorage():
    def __init__(self, db: DuckDbRef | str | Path):
        match db:
            case str():
                self.__db = DuckDbRef(db)
            case Path():
                self.__db = DuckDbRef(db)
            case DuckDbRef():
                self.__db = db
            case _:
                raise ValueError(f"Invalid database path: {db}")

    def open_db(self, read_only=False):
        return self.__db.open_db(read_only=read_only)

    def setup_db(self):
        """Create the full BGM archive schema"""
        with self.open_db(read_only=False) as conn:
            conn.install_extension("duckpgq", repository="community")
            conn.load_extension("duckpgq")
            conn.execute(_CREATE_TABLE_SQL).fetchone()
            conn.execute(_CREATE_GRAPH_SQL).fetchone()

    def load_all(
        self,
        loader: WikiArchiveLoader,
        *,
        limit=None,
        progress_bar=False,
    ):
        def wrap_iterator(iterator: Iterator) -> Iterator:
            if limit:
                iterator = itertools.islice(iterator, limit)
            if progress_bar:
                from tqdm import tqdm

                yield from tqdm(iterator)
            else:
                yield from iterator

        """Import all data from the loader into the database"""

        self.import_subjects(wrap_iterator(loader.subjects()))

        logger.info("Imported subjects")

        self.import_persons(wrap_iterator(loader.persons()))
        logger.info("Imported persons")

        self.import_characters(wrap_iterator(
            loader.characters()))
        logger.info("Imported characters")

        self.import_episodes(wrap_iterator(loader.episodes()))
        logger.info("Imported episodes")

        self.import_subject_relations(
            wrap_iterator(loader.subject_relations())
        )
        logger.info("Imported subject relations")

        self.import_subject_persons(
            wrap_iterator(loader.subject_persons())
        )
        logger.info("Imported subject persons")

        self.import_subject_characters(
            wrap_iterator(loader.subject_characters())
        )
        logger.info("Imported subject characters")

        self.import_person_characters(
            wrap_iterator(loader.person_characters())
        )
        logger.info("Imported person characters")

    def import_subjects(self, subjects: Iterator[model.Subject]) -> int:
        with contextlib.ExitStack() as stack:
            temp_dir = stack.enter_context(tempfile.TemporaryDirectory())
            conn = stack.enter_context(self.open_db(read_only=False))
            tmp_json = f"{temp_dir}/subjects.jsonl"
            with open(tmp_json, "w") as f:
                for subject in subjects:
                    dic = {
                        "id": subject.id,
                        "type": subject.type.value,
                        "name": subject.name,
                        "name_cn": subject.name_cn,
                        "infobox": subject.infobox,
                        "platform": subject.platform,
                        "summary": subject.summary,
                        "nsfw": subject.nsfw,
                        "score": subject.score,
                        "rank": subject.rank,
                        "date": subject.date,
                        "favorite_wish": subject.favorite.wish,
                        "favorite_done": subject.favorite.done,
                        "favorite_doing": subject.favorite.doing,
                        "favorite_on_hold": subject.favorite.on_hold,
                        "favorite_dropped": subject.favorite.dropped,
                        "series": subject.series,
                    }
                    f.write(json.dumps(dic, ensure_ascii=False) + "\n")
            logging.info("Importing subjects from %s", tmp_json)
            conn.execute(f"""
            COPY Subjects FROM '{tmp_json}'
                         """)
            row = conn.execute(
                "SELECT COUNT(*) AS cnt FROM Subjects").fetchone()
            cnt = cast(int, row[0])  # type: ignore
            logging.info("Imported %d subjects from %s", cnt, tmp_json)
            return cnt

    def import_persons(self, persons: Iterator[model.Person]) -> int:
        with contextlib.ExitStack() as stack:
            temp_dir = stack.enter_context(tempfile.TemporaryDirectory())
            conn = stack.enter_context(self.open_db(read_only=False))
            tmp_json = f"{temp_dir}/persons.jsonl"
            with open(tmp_json, "w") as f:
                for person in persons:
                    dic = {
                        "id": person.id,
                        "name": person.name,
                        "type": person.type.value,
                        "career": person.career,
                        "infobox": person.infobox,
                        "summary": person.summary,
                        "comments": person.comments,
                        "collects": person.collects,
                    }
                    f.write(json.dumps(dic, ensure_ascii=False) + "\n")
            logging.info("Importing persons from %s", tmp_json)
            conn.execute(f"""
            COPY Persons FROM '{tmp_json}'
                         """)
            logging.info("Imported persons from %s", tmp_json)
            (count) = conn.execute("SELECT COUNT(*) AS cnt FROM Persons").fetchone()
            return cast(int, count)

    def import_characters(self, characters: Iterator[model.Character]) -> int:
        with contextlib.ExitStack() as stack:
            temp_dir = stack.enter_context(tempfile.TemporaryDirectory())
            conn = stack.enter_context(self.open_db(read_only=False))
            tmp_json = f"{temp_dir}/characters.jsonl"
            with open(tmp_json, "w") as f:
                for character in characters:
                    dic = {
                        "id": character.id,
                        "role": character.role.value,
                        "name": character.name,
                        "infobox": character.infobox,
                        "summary": character.summary,
                        "comments": character.comments,
                        "collects": character.collects,
                    }
                    f.write(json.dumps(dic, ensure_ascii=False) + "\n")
            logging.info("Importing characters from %s", tmp_json)
            conn.execute(f"""
            COPY Characters FROM '{tmp_json}'
                         """)
            logging.info("Imported characters from %s", tmp_json)
            (count) = conn.execute(
                "SELECT COUNT(*) AS cnt FROM Characters").fetchone()
            return cast(int, count)

    def import_episodes(self, episodes: Iterator[model.Episode]) -> int:
        with contextlib.ExitStack() as stack:
            temp_dir = stack.enter_context(tempfile.TemporaryDirectory())
            conn = stack.enter_context(self.open_db(read_only=False))
            tmp_json = f"{temp_dir}/episodes.jsonl"
            with open(tmp_json, "w") as f:
                for episode in episodes:
                    dic = {
                        "id": episode.id,
                        "name": episode.name,
                        "name_cn": episode.name_cn,
                        "description": episode.description,
                        "airdate": episode.airdate,
                        "disc": episode.disc,
                        "duration": episode.duration,
                        "subject_id": episode.subject_id,
                        "sort": episode.sort,
                        "type": episode.type.value,
                    }
                    f.write(json.dumps(dic, ensure_ascii=False) + "\n")
            logging.info("Importing episodes from %s", tmp_json)
            conn.execute(f"""
            COPY Episodes FROM '{tmp_json}'
                         """)
            logging.info("Imported episodes from %s", tmp_json)
            (count) = conn.execute("SELECT COUNT(*) AS cnt FROM Episodes").fetchone()
            return cast(int, count)

    def import_subject_relations(self, relations: Iterator[model.SubjectRelation]) -> int:
        with contextlib.ExitStack() as stack:
            temp_dir = stack.enter_context(tempfile.TemporaryDirectory())
            conn = stack.enter_context(self.open_db(read_only=False))
            tmp_json = f"{temp_dir}/subject_relations.jsonl"
            with open(tmp_json, "w") as f:
                for relation in relations:
                    dic = {
                        "subject_id": relation.subject_id,
                        "relation_type": relation.relation_type.value,
                        "related_subject_id": relation.related_subject_id,
                        "order_idx": relation.order,
                    }
                    f.write(json.dumps(dic, ensure_ascii=False) + "\n")
            logging.info("Importing subject relations from %s", tmp_json)
            conn.execute(f"""
            COPY SubjectRelation FROM '{tmp_json}'
                         """)
            logging.info("Imported subject relations from %s", tmp_json)
            (count) = conn.execute(
                "SELECT COUNT(*) AS cnt FROM SubjectRelation").fetchone()
            return cast(int, count)

    def import_subject_persons(self, relations: Iterator[model.SubjectPerson]) -> int:
        with contextlib.ExitStack() as stack:
            temp_dir = stack.enter_context(tempfile.TemporaryDirectory())
            conn = stack.enter_context(self.open_db(read_only=False))
            tmp_json = f"{temp_dir}/subject_persons.jsonl"
            with open(tmp_json, "w") as f:
                for relation in relations:
                    dic = {
                        "person_id": relation.person_id,
                        "subject_id": relation.subject_id,
                        "position": relation.position.value,
                    }
                    f.write(json.dumps(dic, ensure_ascii=False) + "\n")
            logging.info("Importing subject persons from %s", tmp_json)
            conn.execute(f"""
            COPY SubjectPersons FROM '{tmp_json}'
                         """)
            logging.info("Imported subject persons from %s", tmp_json)
            (count) = conn.execute(
                "SELECT COUNT(*) AS cnt FROM SubjectPersons").fetchone()
            return cast(int, count)

    def import_subject_characters(self, relations: Iterator[model.SubjectCharacter]) -> int:
        with contextlib.ExitStack() as stack:
            temp_dir = stack.enter_context(tempfile.TemporaryDirectory())
            conn = stack.enter_context(self.open_db(read_only=False))
            tmp_json = f"{temp_dir}/subject_characters.jsonl"
            with open(tmp_json, "w") as f:
                for relation in relations:
                    dic = {
                        "character_id": relation.character_id,
                        "subject_id": relation.subject_id,
                        "type": relation.type.value,
                        "order_idx": relation.order,
                    }
                    f.write(json.dumps(dic, ensure_ascii=False) + "\n")
            logging.info("Importing subject characters from %s", tmp_json)
            conn.execute(f"""
            COPY SubjectCharacter FROM '{tmp_json}'
                         """)
            logging.info("Imported subject characters from %s", tmp_json)
            (count) = conn.execute(
                "SELECT COUNT(*) AS cnt FROM SubjectCharacter").fetchone()
            return cast(int, count)

    def import_person_characters(self, relations: Iterator[model.PersonCharacter]) -> int:
        with contextlib.ExitStack() as stack:
            temp_dir = stack.enter_context(tempfile.TemporaryDirectory())
            conn = stack.enter_context(self.open_db(read_only=False))
            tmp_json = f"{temp_dir}/person_characters.jsonl"
            with open(tmp_json, "w") as f:
                for relation in relations:
                    dic = {
                        "person_id": relation.person_id,
                        "subject_id": relation.subject_id,
                        "character_id": relation.character_id,
                        "summary": relation.summary,
                    }
                    f.write(json.dumps(dic, ensure_ascii=False) + "\n")
            logging.info("Importing person characters from %s", tmp_json)
            conn.execute(f"""
            COPY PersonCharacter FROM '{tmp_json}'
                         """)
            logging.info("Imported person characters from %s", tmp_json)
            (count) = conn.execute(
                "SELECT COUNT(*) AS cnt FROM PersonCharacter").fetchone()
            return cast(int, count)


_CREATE_TABLE_SQL = """
-- node tables

CREATE TABLE IF NOT EXISTS Subjects(
    id INTEGER PRIMARY KEY,
    type INTEGER NOT NULL,
    name VARCHAR NOT NULL,
    name_cn VARCHAR,
    infobox TEXT,
    platform INTEGER,
    summary TEXT,
    nsfw BOOLEAN DEFAULT FALSE,
    score DOUBLE,
    rank INTEGER,
    date VARCHAR,
    favorite_wish INTEGER DEFAULT 0,
    favorite_done INTEGER DEFAULT 0,
    favorite_doing INTEGER DEFAULT 0,
    favorite_on_hold INTEGER DEFAULT 0,
    favorite_dropped INTEGER DEFAULT 0,
    series BOOLEAN DEFAULT FALSE,
    comments INTEGER DEFAULT 0,
    collects INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Persons(
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    type INTEGER NOT NULL,
    career TEXT[], -- JSON array of career strings
    infobox TEXT,
    summary TEXT,
    comments INTEGER DEFAULT 0,
    collects INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Characters(
    id INTEGER PRIMARY KEY,
    role INTEGER NOT NULL,
    name VARCHAR NOT NULL,
    infobox TEXT,
    summary TEXT,
    comments INTEGER DEFAULT 0,
    collects INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Episodes(
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    name_cn VARCHAR,
    description TEXT,
    airdate VARCHAR,
    disc INTEGER,
    duration VARCHAR,
    subject_id INTEGER NOT NULL,
    sort DOUBLE,
    type INTEGER NOT NULL,
    -- FOREIGN KEY(subject_id) REFERENCES Subjects(id)
);

-- edge tables

CREATE TABLE IF NOT EXISTS SubjectRelation(
    subject_id INTEGER NOT NULL,
    relation_type INTEGER NOT NULL,
    related_subject_id INTEGER NOT NULL,
    order_idx INTEGER DEFAULT 0,
    -- PRIMARY KEY(subject_id, related_subject_id, relation_type),
    -- FOREIGN KEY(subject_id) REFERENCES Subjects(id),
    -- FOREIGN KEY(related_subject_id) REFERENCES Subjects(id)
);

CREATE TABLE IF NOT EXISTS SubjectPersons(
    person_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    -- PRIMARY KEY(person_id, subject_id, position),
    -- FOREIGN KEY(person_id) REFERENCES Persons(id),
    -- FOREIGN KEY(subject_id) REFERENCES Subjects(id)
);

CREATE TABLE IF NOT EXISTS SubjectCharacter(
    character_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    type INTEGER NOT NULL,
    order_idx INTEGER DEFAULT 0,
    -- PRIMARY KEY(character_id, subject_id),
    -- FOREIGN KEY(character_id) REFERENCES Characters(id),
    -- FOREIGN KEY(subject_id) REFERENCES Subjects(id)
);

CREATE TABLE IF NOT EXISTS PersonCharacter(
    person_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    character_id INTEGER NOT NULL,
    summary TEXT,
    -- PRIMARY KEY(person_id, subject_id, character_id),
    -- FOREIGN KEY(person_id) REFERENCES Persons(id),
    -- FOREIGN KEY(subject_id) REFERENCES Subjects(id),
    -- FOREIGN KEY(character_id) REFERENCES Characters(id)
);
"""

_CREATE_GRAPH_SQL = """
CREATE OR REPLACE PROPERTY GRAPH bgm_graph  

-- vertax table: table name becomes vertex label
VERTEX TABLES (Subjects, Persons, Characters)  

EDGE TABLES (
  SubjectRelation
    SOURCE KEY (subject_id) REFERENCES Subjects (id)
    DESTINATION KEY (related_subject_id) REFERENCES Subjects (id)  
    PROPERTIES (relation_type)
    LABEL s2s,

  PersonCharacter
    SOURCE KEY (person_id) REFERENCES Persons (id)
    DESTINATION KEY (character_id) REFERENCES Characters (id)
    PROPERTIES (summary)
    LABEL p2c,

  SubjectPersons
    SOURCE KEY (person_id) REFERENCES Persons (id)
    DESTINATION KEY (subject_id) REFERENCES Subjects (id)
    PROPERTIES (position)
    LABEL s2p,

  SubjectCharacter
    SOURCE KEY (character_id) REFERENCES Characters (id)
    DESTINATION KEY (subject_id) REFERENCES Subjects (id)
    PROPERTIES (type)
    LABEL s2c
);
"""
