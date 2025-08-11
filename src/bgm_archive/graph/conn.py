import itertools
import pandas as pd
from pathlib import Path
from typing import Iterator, ContextManager, AsyncContextManager
import duckdb
from pydantic import BaseModel
from bgm_archive.loader import WikiArchiveLoader, model
import contextlib

import logging

logger = logging.getLogger(__name__)


class DuckWrapper():
    def __init__(self, path: str | Path):
        self._path = Path(path)
        self._conn: duckdb.DuckDBPyConnection = None  # type: ignore

    def peek_table(self, table_name: str) -> pd.DataFrame:
        with self.open_db(read_only=True) as conn:
            result = conn.execute(f"SELECT * FROM {table_name} LIMIT 10").df()
            return result
    def count_table(self, table_name: str) -> int:
        with self.open_db(read_only=True) as conn:
            result = conn.execute(
                f"SELECT COUNT(*) FROM {table_name}").fetchone()
            return result[0] if result else 0

    def list_extensions(self) -> duckdb.DuckDBPyConnection:
        with self.open_db(read_only=True) as conn:
            return conn.execute("SELECT * FROM duckdb_extensions();")

    def open_db(self, read_only=False) -> ContextManager[duckdb.DuckDBPyConnection]:
        @contextlib.contextmanager
        def create():
            assert self._conn is None, "Connection already open"
            db = duckdb.connect(self._path, read_only=read_only)
            self._conn = db
            yield db  # type: ignore
            self._conn = None  # type: ignore
            db.close()
        return create()


class BgmGraph(DuckWrapper):

    def setup_db(self):
        with self.open_db() as conn:
            conn.install_extension("duckpgq", repository="community")
            conn.load_extension("duckpgq")

    def create_bgm_schema(self):
        """Create the full BGM archive schema"""
        with self.open_db(read_only=False) as conn:
            conn.execute(_CREATE_TABLE_SQL).fetchall()

    def import_all(self, loader: WikiArchiveLoader, *, chunk_size=50000, limit=None, progress_bar=False):

        def wrap_iterator(iterator: Iterator) -> Iterator:
            if limit:
                iterator = itertools.islice(iterator, limit)
            if progress_bar:
                from tqdm import tqdm
                yield from tqdm(iterator)
            else:
                yield from iterator
        """Import all data from the loader into the database"""

        with self.open_db(read_only=False):
            self.import_subjects(wrap_iterator(loader.subjects()), chunk_size)

            logger.info("Imported subjects")

            self.import_persons(wrap_iterator(loader.persons()), chunk_size)
            logger.info("Imported persons")

            self.import_characters(wrap_iterator(
                loader.characters()), chunk_size)
            logger.info("Imported characters")

            self.import_episodes(wrap_iterator(loader.episodes()), chunk_size)
            logger.info("Imported episodes")

            self.import_subject_relations(wrap_iterator(
                loader.subject_relations()), chunk_size)
            logger.info("Imported subject relations")

            self.import_subject_persons(wrap_iterator(
                loader.subject_persons()), chunk_size)
            logger.info("Imported subject persons")

            self.import_subject_characters(wrap_iterator(
                loader.subject_characters()), chunk_size)
            logger.info("Imported subject characters")

            self.import_person_characters(wrap_iterator(
                loader.person_characters()), chunk_size)
            logger.info("Imported person characters")

    def import_subjects(self, subjects: Iterator[model.Subject], chunk_size=1000):
        for chunk in itertools.batched(subjects, chunk_size):
            self._conn.executemany(
                """INSERT INTO Subjects
                  (id, type, name, name_cn, infobox, platform, summary, nsfw, score, rank, "date", favorite_wish, favorite_done, favorite_doing, favorite_on_hold, favorite_dropped, series)
                  VALUES
                  (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", [
                    (
                        subject.id,
                        subject.type.value,
                        subject.name,
                        subject.name_cn,
                        subject.infobox,
                        subject.platform,
                        subject.summary,
                        subject.nsfw,
                        subject.score,
                        subject.rank,
                        subject.date,
                        subject.favorite.wish,
                        subject.favorite.done,
                        subject.favorite.doing,
                        subject.favorite.on_hold,
                        subject.favorite.dropped,
                        subject.series,
                    )
                    for subject in chunk
                ])

    def import_persons(self, persons: Iterator[model.Person], chunk_size=1000):
        for chunk in itertools.batched(persons, chunk_size):
            self._conn.executemany(
                """INSERT INTO Persons
                  (id, name, type, career, infobox, summary, comments, collects)
                  VALUES
                  (?, ?, ?, ?, ?, ?, ?, ?)""", [
                    (
                        person.id,
                        person.name,
                        person.type.value,
                        person.career,
                        person.infobox,
                        person.summary,
                        person.comments,
                        person.collects,
                    )
                    for person in chunk
                ])

    def import_characters(self, characters: Iterator[model.Character], chunk_size=1000):
        for chunk in itertools.batched(characters, chunk_size):
            self._conn.executemany(
                """INSERT INTO Characters
                  (id, role, name, infobox, summary, comments, collects)
                  VALUES
                  (?, ?, ?, ?, ?, ?, ?)""", [
                    (
                        character.id,
                        character.role.value,
                        character.name,
                        character.infobox,
                        character.summary,
                        character.comments,
                        character.collects,
                    )
                    for character in chunk
                ])

    def import_episodes(self, episodes: Iterator[model.Episode], chunk_size=1000):
        for chunk in itertools.batched(episodes, chunk_size):
            self._conn.executemany(
                """INSERT INTO Episodes
                  (id, name, name_cn, description, airdate, disc, duration, subject_id, sort, type)
                  VALUES
                  (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", [
                    (
                        episode.id,
                        episode.name,
                        episode.name_cn,
                        episode.description,
                        episode.airdate,
                        episode.disc,
                        episode.duration,
                        episode.subject_id,
                        episode.sort,
                        episode.type.value,
                    )
                    for episode in chunk
                ])

    def import_subject_relations(self, relations: Iterator[model.SubjectRelation], chunk_size=1000):
        for chunk in itertools.batched(relations, chunk_size):
            self._conn.executemany(
                """INSERT INTO SubjectRelation
                  (subject_id, relation_type, related_subject_id, order_idx)
                  VALUES
                  (?, ?, ?, ?)""", [
                    (
                        relation.subject_id,
                        relation.relation_type.value,
                        relation.related_subject_id,
                        relation.order,
                    )
                    for relation in chunk
                ])

    def import_subject_persons(self, relations: Iterator[model.SubjectPerson], chunk_size=1000):
        for chunk in itertools.batched(relations, chunk_size):
            self._conn.executemany(
                """INSERT INTO SubjectPersons
                  (person_id, subject_id, position)
                  VALUES
                  (?, ?, ?)""", [
                    (
                        relation.person_id,
                        relation.subject_id,
                        relation.position.value,
                    )
                    for relation in chunk
                ])

    def import_subject_characters(self, relations: Iterator[model.SubjectCharacter], chunk_size=1000):
        for chunk in itertools.batched(relations, chunk_size):
            self._conn.executemany(
                """INSERT INTO SubjectCharacter
                  (character_id, subject_id, type, order_idx)
                  VALUES
                  (?, ?, ?, ?)""", [
                    (
                        relation.character_id,
                        relation.subject_id,
                        relation.type.value,
                        relation.order,
                    )
                    for relation in chunk
                ])

    def import_person_characters(self, relations: Iterator[model.PersonCharacter], chunk_size=1000):
        for chunk in itertools.batched(relations, chunk_size):
            self._conn.executemany(
                """INSERT INTO PersonCharacter
                  (person_id, subject_id, character_id, summary)
                  VALUES
                  (?, ?, ?, ?)""", [
                    (
                        relation.person_id,
                        relation.subject_id,
                        relation.character_id,
                        relation.summary,
                    )
                    for relation in chunk
                ])


_CREATE_TABLE_SQL = """
-- node tables

CREATE TABLE IF NOT EXISTS Subjects (
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

CREATE TABLE IF NOT EXISTS Persons (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    type INTEGER NOT NULL,
    career TEXT[], -- JSON array of career strings
    infobox TEXT,
    summary TEXT,
    comments INTEGER DEFAULT 0,
    collects INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Characters (
    id INTEGER PRIMARY KEY,
    role INTEGER NOT NULL,
    name VARCHAR NOT NULL,
    infobox TEXT,
    summary TEXT,
    comments INTEGER DEFAULT 0,
    collects INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Episodes (
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
    -- FOREIGN KEY (subject_id) REFERENCES Subjects(id)
);

-- edge tables

CREATE TABLE IF NOT EXISTS SubjectRelation (
    subject_id INTEGER NOT NULL,
    relation_type INTEGER NOT NULL,
    related_subject_id INTEGER NOT NULL,
    order_idx INTEGER DEFAULT 0,
    -- PRIMARY KEY (subject_id, related_subject_id, relation_type),
    -- FOREIGN KEY (subject_id) REFERENCES Subjects(id),
    -- FOREIGN KEY (related_subject_id) REFERENCES Subjects(id)
);

CREATE TABLE IF NOT EXISTS SubjectPersons (
    person_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    -- PRIMARY KEY (person_id, subject_id, position),
    -- FOREIGN KEY (person_id) REFERENCES Persons(id),
    -- FOREIGN KEY (subject_id) REFERENCES Subjects(id)
);

CREATE TABLE IF NOT EXISTS SubjectCharacter (
    character_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    type INTEGER NOT NULL,
    order_idx INTEGER DEFAULT 0,
    -- PRIMARY KEY (character_id, subject_id),
    -- FOREIGN KEY (character_id) REFERENCES Characters(id),
    -- FOREIGN KEY (subject_id) REFERENCES Subjects(id)
);

CREATE TABLE IF NOT EXISTS PersonCharacter (
    person_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    character_id INTEGER NOT NULL,
    summary TEXT,
    -- PRIMARY KEY (person_id, subject_id, character_id),
    -- FOREIGN KEY (person_id) REFERENCES Persons(id),
    -- FOREIGN KEY (subject_id) REFERENCES Subjects(id),
    -- FOREIGN KEY (character_id) REFERENCES Characters(id)
);
"""
