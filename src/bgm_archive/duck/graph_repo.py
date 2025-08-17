from tkinter import NO
import bgm_archive.loader.model as m
from .conn import DuckDbRef
from pathlib import Path
from .data import GraphEdge, GraphNode
from .rdb_repo import RdbRepository


class GraphRepository:
    def __init__(self, db: DuckDbRef | str | Path, rdb: RdbRepository):
        self.__db = DuckDbRef.from_db(db)
        self.__rdb = rdb

    def expand_s2s(self, subject_id: int) -> list[GraphEdge]:
        """Expand s2s (subject to subject) edges for a given subject ID."""
        assert isinstance(
            subject_id, int) and subject_id > 0, "subject_id must be a positive integer"
        query = f"""
            SELECT s1_id, s2_id, relation_type
            FROM GRAPH_TABLE(
                bgm_graph
                MATCH (s1: Subjects)-[e: s2s]-(s2: Subjects)
                COLUMNS (s1.id AS s1_id, e.relation_type AS relation_type, s2.id AS s2_id)
            )
            WHERE s1_id = {subject_id}
            """
        with self.__db.open_db(read_only=False) as conn:

            subject1 = self.__rdb.find_subject_by_id(subject_id)
            if not subject1:
                return []

            result: list[tuple[int, int, int]] = conn.execute(
                query, parameters=[]).fetchall()

            subject2s = self.__rdb.find_subjects_by_ids(
                list(set([row[1] for row in result])))

            subject2_by_id = {s.id: s for s in subject2s}

            return [
                GraphEdge(
                    from_subject=subject1,
                    to_subject=subject2_by_id.get(_s2id, None),
                    s2s_relation_type=m.SubjectRelationType(
                        subject_relation_type)
                ) for _s1id, subject_relation_type, _s2id in result
            ]

    def expand_s2c(self, subject_id: int) -> list[GraphEdge]:
        """Expand s2c (subject to character) edges for a given subject ID."""
        assert isinstance(
            subject_id, int) and subject_id > 0, "subject_id must be a positive integer"
        query = f"""
            SELECT s_id AS subject_id, character_id AS character_id, type
            FROM GRAPH_TABLE(
                bgm_graph
                MATCH (s: Subjects)-[e: s2c]-(c: Characters)
                COLUMNS (s.id AS s_id, e.type AS type, c.id AS character_id)
            )
            WHERE s_id = {subject_id}
            """
        with self.__db.open_db(read_only=False) as conn:
            subject = self.__rdb.find_subject_by_id(subject_id)
            if not subject:
                return []

            result: list[tuple[int, int, int]] = conn.execute(
                query, parameters=[]).fetchall()

            character_ids = [row[1] for row in result]
            characters = self.__rdb.find_characters_by_ids(character_ids)

            character_by_id = {c.id: c for c in characters}

            return [
                GraphEdge(
                    from_subject=subject,
                    to_character=character_by_id.get(_cid, None),
                    s2c_type=m.SubjectCharacterType(_type)
                ) for _sid, _cid, _type in result
            ]

    def expand_s2p(self, subject_id: int) -> list[GraphEdge]:
        """Expand s2p (subject to person) edges for a given subject ID."""
        assert isinstance(
            subject_id, int) and subject_id > 0, "subject_id must be a positive integer"
        query = f"""
            SELECT subject_id AS subject_id, person_id AS person_id, position
            FROM GRAPH_TABLE(
                bgm_graph
                MATCH (s: Subjects)-[e: s2p]-(p: Persons)
                COLUMNS (s.id AS subject_id, e.position AS position, p.id AS person_id)
            )
            WHERE subject_id = {subject_id}
            """
        with self.__db.open_db(read_only=False) as conn:
            subject = self.__rdb.find_subject_by_id(subject_id)
            if not subject:
                return []

            result: list[tuple[int, int, int]] = conn.execute(
                query, parameters=[]).fetchall()

            person_ids = [row[1] for row in result]
            persons = self.__rdb.find_people_by_ids(person_ids)

            person_by_id = {p.id: p for p in persons}

            return [
                GraphEdge(
                    from_subject=subject,
                    to_person=person_by_id.get(_pid, None),
                    s2p_position=m.SubjectPersonType.from_value(_position)
                ) for _sid, _pid, _position in result
            ]

    def expand_c2p(self, character_id: int) -> list[GraphEdge]:
        """Expand c2p (character to person) edges for a given character ID."""
        assert isinstance(
            character_id, int) and character_id > 0, "character_id must be a positive integer"
        query = f"""
            SELECT character_id, person_id, summary
            FROM GRAPH_TABLE(
                bgm_graph
                MATCH (c: Characters)-[e: p2c]-(p: Persons)
                COLUMNS (c.id AS character_id, e.summary AS summary, p.id AS person_id)
            )
            WHERE character_id = {character_id}
            """
        with self.__db.open_db(read_only=False) as conn:
            character = self.__rdb.find_character_by_id(character_id)
            if not character:
                return []

            result: list[tuple[int, int, str]] = conn.execute(
                query, parameters=[]).fetchall()

            person_ids = [row[1] for row in result]
            persons = self.__rdb.find_people_by_ids(person_ids)

            person_by_id = {p.id: p for p in persons}

            return [
                GraphEdge(
                    from_character=character,
                    to_person=person_by_id.get(_pid, None),
                    p2c_summary=_summary,
                ) for _cid, _pid, _summary in result
            ]

    def expand_c2s(self, character_id: int) -> list[GraphEdge]:
        """Expand c2s (character to subject) edges for a given character ID."""
        assert isinstance(
            character_id, int) and character_id > 0, "character_id must be a positive integer"
        query = f"""
            SELECT character_id, subject_id, type
            FROM GRAPH_TABLE(
                bgm_graph
                MATCH (c: Characters)-[e: s2c]-(s: Subjects)
                COLUMNS (c.id AS character_id, e.type AS type, s.id AS subject_id)
            )
            WHERE character_id = {character_id}
            """
        with self.__db.open_db(read_only=False) as conn:
            character = self.__rdb.find_character_by_id(character_id)
            if not character:
                return []

            result: list[tuple[int, int, int]] = conn.execute(
                query, parameters=[]).fetchall()

            subject_ids = [row[1] for row in result]
            subjects = self.__rdb.find_subjects_by_ids(subject_ids)

            subject_by_id = {s.id: s for s in subjects}

            return [
                GraphEdge(
                    from_character=character,
                    to_subject=subject_by_id.get(_sid, None),
                    s2c_type=m.SubjectCharacterType(_type)
                ) for _cid, _sid, _type in result
            ]

    def expand_p2s(self, person_id: int) -> list[GraphEdge]:
        """Expand p2s (person to subject) edges for a given person ID."""
        assert isinstance(
            person_id, int) and person_id > 0, "person_id must be a positive integer"
        query = f"""
            SELECT person_id, subject_id, position
            FROM GRAPH_TABLE(
                bgm_graph
                MATCH (p: Persons)-[e: s2p]-(s: Subjects)
                COLUMNS (p.id AS person_id, e.position AS position, s.id AS subject_id)
            )
            WHERE person_id = {person_id}
            """
        with self.__db.open_db(read_only=False) as conn:
            person = self.__rdb.find_person_by_id(person_id)
            if not person:
                return []

            result: list[tuple[int, int, int]] = conn.execute(
                query, parameters=[]).fetchall()

            subject_ids = [row[1] for row in result]
            subjects = self.__rdb.find_subjects_by_ids(subject_ids)

            subject_by_id = {s.id: s for s in subjects}

            return [
                GraphEdge(
                    from_person=person,
                    to_subject=subject_by_id.get(_sid, None),
                    s2p_position=m.SubjectPersonType.from_value(_position)
                ) for _pid, _sid, _position in result
            ]
