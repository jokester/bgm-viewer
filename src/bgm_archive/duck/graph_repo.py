import bgm_archive.loader.model as m
from .conn import DuckDbRef
from pathlib import Path
from .data import GraphEdge
from .rdb_repo import RdbRepository
import logging

logger = logging.getLogger(__name__)


class GraphRepository:
    def __init__(self, db: DuckDbRef | str | Path, rdb: RdbRepository):
        self.__db = DuckDbRef.from_db(db)
        self.__rdb = rdb

    def expand_s2s(self, from_subject: m.Subject) -> list[GraphEdge]:
        """Expand s2s (subject to subject) edges for a given subject ID."""
        assert isinstance(
            from_subject, m.Subject)
        query = f"""
            SELECT s1_id, s2_id, relation_type
            FROM GRAPH_TABLE(
                bgm_graph
                MATCH (s1: Subjects)-[e: s2s]-(s2: Subjects)
                COLUMNS (s1.id AS s1_id, e.relation_type AS relation_type, s2.id AS s2_id)
            )
            WHERE s1_id = {from_subject.id}
            """
        with self.__db.open_db(read_only=False) as conn:

            result: list[tuple[int, int, int]] = conn.execute(
                query, parameters=[]).fetchall()

            subject2s = self.__rdb.find_subjects_by_ids(
                list(set([row[1] for row in result])))

            subject2_by_id = {s.id: s for s in subject2s}

            edges = [
                GraphEdge(
                    to_subject=subject2_by_id.get(_s2id, None),
                    s2s_relation_type=m.SubjectRelationType(
                        subject_relation_type)
                ) for _s1id, _s2id, subject_relation_type in result
            ]
            return edges

    def expand_s2c(self, subject: m.Subject) -> list[GraphEdge]:
        """Expand s2c (subject to character) edges for a given subject ID."""
        assert isinstance(subject, m.Subject)
        query = f"""
            SELECT s_id AS subject_id, character_id AS character_id, type
            FROM GRAPH_TABLE(
                bgm_graph
                MATCH (s: Subjects)-[e: s2c]-(c: Characters)
                COLUMNS (s.id AS s_id, e.type AS type, c.id AS character_id)
            )
            WHERE s_id = {subject.id}
            """
        with self.__db.open_db(read_only=False) as conn:
            result: list[tuple[int, int, int]] = conn.execute(
                query, parameters=[]).fetchall()

            character_ids = [row[1] for row in result]
            characters = self.__rdb.find_characters_by_ids(character_ids)

            character_by_id = {c.id: c for c in characters}

            edges = [
                GraphEdge(
                    to_character=character_by_id.get(_cid, None),
                    s2c_type=m.SubjectCharacterType(_type)
                ) for _sid, _cid, _type in result
            ]
            return edges

    def expand_s2p(self, subject: m.Subject) -> list[GraphEdge]:
        """Expand s2p (subject to person) edges for a given subject."""
        assert isinstance(subject, m.Subject)
        query = f"""
            SELECT subject_id AS subject_id, person_id AS person_id, position
            FROM GRAPH_TABLE(
                bgm_graph
                MATCH (s: Subjects)-[e: s2p]-(p: Persons)
                COLUMNS (s.id AS subject_id, e.position AS position, p.id AS person_id)
            )
            WHERE subject_id = {subject.id}
            """
        with self.__db.open_db(read_only=False) as conn:
            result: list[tuple[int, int, int]] = conn.execute(
                query, parameters=[]).fetchall()

            person_ids = [row[1] for row in result]
            persons = self.__rdb.find_people_by_ids(person_ids)

            person_by_id = {p.id: p for p in persons}

            edges = [
                GraphEdge(
                    to_person=person_by_id.get(_pid, None),
                    s2p_position=m.SubjectPersonType.from_value(_position)
                ) for _sid, _pid, _position in result
            ]
            return edges

    def expand_c2p(self, character: m.Character) -> list[GraphEdge]:
        """Expand c2p (character to person) edges for a given character."""
        assert isinstance(character, m.Character)
        query = f"""
            SELECT character_id, person_id, summary
            FROM GRAPH_TABLE(
                bgm_graph
                MATCH (c: Characters)-[e: p2c]-(p: Persons)
                COLUMNS (c.id AS character_id, e.summary AS summary, p.id AS person_id)
            )
            WHERE character_id = {character.id}
            """
        with self.__db.open_db(read_only=False) as conn:
            result: list[tuple[int, int, str]] = conn.execute(
                query, parameters=[]).fetchall()
            print(
                f"Found {len(result)} c2p edges for character {character.id}")

            person_ids = [row[1] for row in result]
            persons = self.__rdb.find_people_by_ids(person_ids)

            person_by_id = {p.id: p for p in persons}

            edges = [
                GraphEdge(
                    to_person=person_by_id.get(_pid, None),
                    p2c_summary=_summary,
                ) for _cid, _pid, _summary in result
            ]
            return edges

    def expand_c2s(self, character: m.Character) -> list[GraphEdge]:
        """Expand c2s (character to subject) edges for a given character."""
        assert isinstance(character, m.Character)
        query = f"""
            SELECT character_id, subject_id, type
            FROM GRAPH_TABLE(
                bgm_graph
                MATCH (c: Characters)-[e: s2c]-(s: Subjects)
                COLUMNS (c.id AS character_id, e.type AS type, s.id AS subject_id)
            )
            WHERE character_id = {character.id}
            """
        with self.__db.open_db(read_only=False) as conn:
            result: list[tuple[int, int, int]] = conn.execute(
                query, parameters=[]).fetchall()

            subject_ids = [row[1] for row in result]
            subjects = self.__rdb.find_subjects_by_ids(subject_ids)

            subject_by_id = {s.id: s for s in subjects}

            edges = [
                GraphEdge(
                    to_subject=subject_by_id.get(_sid, None),
                    s2c_type=m.SubjectCharacterType(_type)
                ) for _cid, _sid, _type in result
            ]
            return edges

    def expand_p2s(self, person: m.Person) -> list[GraphEdge]:
        """Expand p2s (person to subject) edges for a given person."""
        assert isinstance(person, m.Person)
        query = f"""
            SELECT person_id, subject_id, position
            FROM GRAPH_TABLE(
                bgm_graph
                MATCH (p: Persons)-[e: s2p]-(s: Subjects)
                COLUMNS (p.id AS person_id, e.position AS position, s.id AS subject_id)
            )
            WHERE person_id = {person.id}
            """
        with self.__db.open_db(read_only=False) as conn:
            result: list[tuple[int, int, int]] = conn.execute(
                query, parameters=[]).fetchall()

            subject_ids = [row[1] for row in result]
            subjects = self.__rdb.find_subjects_by_ids(subject_ids)

            subject_by_id = {s.id: s for s in subjects}

            edges = [
                GraphEdge(
                    to_subject=subject_by_id.get(_sid, None),
                    s2p_position=m.SubjectPersonType.from_value(_position)
                ) for _pid, _sid, _position in result
            ]
            return edges

    def expand_p2c(self, person: m.Person) -> list[GraphEdge]:
        """Expand p2c (person to character) edges for a given person."""
        assert isinstance(person, m.Person)
        query = f"""
            SELECT person_id, character_id, summary
            FROM GRAPH_TABLE(
                bgm_graph
                MATCH (p: Persons)-[e: p2c]-(c: Characters)
                COLUMNS (p.id AS person_id, e.summary AS summary, c.id AS character_id)
            )
            WHERE person_id = {person.id}
            """
        with self.__db.open_db(read_only=False) as conn:
            result: list[tuple[int, int, str]] = conn.execute(
                query, parameters=[]).fetchall()

            character_ids = [row[1] for row in result]
            characters = self.__rdb.find_characters_by_ids(character_ids)

            character_by_id = {c.id: c for c in characters}

            edges = [
                GraphEdge(
                    to_character=character_by_id.get(_cid, None),
                    p2c_summary=_summary,
                ) for _pid, _cid, _summary in result
            ]
            return edges
