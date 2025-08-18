import bgm_archive.loader.model as m
from .conn import DuckDbRef
from pathlib import Path
from .data import GraphEdge
from .rdb_repo import RdbRepository, person_row_to_model, subject_row_to_model, character_row_to_model
import logging
import pandas as pd

logger = logging.getLogger(__name__)


_ctes = """
Engagements AS (
    SELECT Persons p, Subjects s, Characters c, PersonCharacter pc
    FROM PersonCharacter
    INNER JOIN Persons ON PersonCharacter.person_id = Persons.id
    INNER JOIN Subjects ON PersonCharacter.subject_id = Subjects.id
    INNER JOIN Characters ON PersonCharacter.character_id = Characters.id
),
S2C AS (
    SELECT Subjects s, Characters c, SubjectCharacter sc
    FROM SubjectCharacter
    INNER JOIN Subjects ON SubjectCharacter.subject_id = Subjects.id
    INNER JOIN Characters ON SubjectCharacter.character_id = Characters.id
),
S2P AS (
    SELECT Subjects s, Persons p, SubjectPersons sp
    FROM SubjectPersons
    INNER JOIN Subjects ON SubjectPersons.subject_id = Subjects.id
    INNER JOIN Persons ON SubjectPersons.person_id = Persons.id
),
S2S AS (
    SELECT s1, s2, SubjectRelation sr
    FROM SubjectRelation
    INNER JOIN Subjects s1 ON SubjectRelation.subject_id = s1.id
    INNER JOIN Subjects s2 ON SubjectRelation.related_subject_id = s2.id
)
"""


class GraphRepository:
    """Provide "graph expansion" methods to query a graph. A expand_* call returns a list of GraphEdge"""
    def __init__(self, db: DuckDbRef | str | Path, rdb: RdbRepository):
        self.__db = DuckDbRef.from_db(db)
        self.__rdb = rdb

    def expand_s2s(self, from_subject: m.Subject) -> list[GraphEdge]:
        """Expand s2s (subject to subject) edges from a given subject."""
        assert isinstance(from_subject, m.Subject)
        query = f"""WITH {_ctes}
            SELECT s2, sr.relation_type
            FROM S2S
            WHERE s1.id = $sId
            """
        with self.__db.open_db(read_only=False) as conn:
            rows: list[tuple[int, int, int]] = conn.execute(
                query, parameters={'sId': from_subject.id}
            ).fetchall()

            edges = [
                GraphEdge(
                    subject1=from_subject,
                    subject2=subject_row_to_model(s2),
                    s2s_relation_type=m.SubjectRelationType(subject_relation_type),
                )
                for s2, subject_relation_type in rows
            ]
            return edges

    def expand_s2p(self, subject1: m.Subject) -> list[GraphEdge]:
        """Expand s2p (subject to persons) edges from a given subject."""
        assert isinstance(subject1, m.Subject)
        query = f"""WITH {_ctes}
            SELECT p, sp.position
            FROM S2P
            WHERE s.id = $sId
            """
        with self.__db.open_db(read_only=False) as conn:
            rows: list[tuple[pd.Series, int]] = conn.execute(
                query, parameters={'sId': subject1.id}
            ).fetchall()

            edges = [
                GraphEdge(
                    subject1=subject1,
                    person=person_row_to_model(p),
                    sp_position=m.SubjectPersonType.from_value(position),
                )
                for p, position in rows
            ]
            return edges
    
    def expand_s2c(self, subject: m.Subject) -> list[GraphEdge]:
        """Expand s2c (subject to characters) edges from a given subject."""
        assert isinstance(subject, m.Subject)
        query = f"""WITH {_ctes}
            SELECT c, sc.type, sc.order_idx
            FROM S2C
            WHERE s.id = $sId
            """
        with self.__db.open_db(read_only=False) as conn:
            rows: list[tuple[pd.Series, int, int]] = conn.execute(
                query, parameters={'sId': subject.id}
            ).fetchall()

            edges = [
                GraphEdge(
                    subject1=subject,
                    character=character_row_to_model(c),
                    sc_type=m.SubjectCharacterType(sc_type),
                    sc_order_idx=order_idx,
                )
                for c, sc_type, order_idx in rows
            ]
            return edges
    
    def expand_s2e(self, subject: m.Subject) -> list[GraphEdge]:
        """Expand s2e (subject to engagements) edges from a given subject."""
        assert isinstance(subject, m.Subject)
        query = f"""WITH {_ctes}
            SELECT p, c, pc.summary
            FROM Engagements
            WHERE s.id = $sId
            """
        with self.__db.open_db(read_only=False) as conn:
            rows: list[tuple[pd.Series, pd.Series, str]] = conn.execute(
                query, parameters={'sId': subject.id}
            ).fetchall()

            edges = [
                GraphEdge(
                    subject1=subject,
                    person=person_row_to_model(p),
                    character=character_row_to_model(c),
                    engagement_summary=summary,
                )
                for p, c, summary in rows
            ]
            return edges

    def expand_c2s(self, character: m.Character) -> list[GraphEdge]:
        """Expand c2s (character to subjects) edges from a given character."""
        assert isinstance(character, m.Character)
        query = f"""WITH {_ctes}
            SELECT s, sc.type, sc.order_idx
            FROM S2C
            WHERE c.id = $cId
            """
        with self.__db.open_db(read_only=False) as conn:
            rows: list[tuple[pd.Series, int, int]] = conn.execute(
                query, parameters={'cId': character.id}
            ).fetchall()

            edges = [
                GraphEdge(
                    character=character,
                    subject2=subject_row_to_model(s),
                    sc_type=m.SubjectCharacterType(sc_type),
                    sc_order_idx=order_idx,
                )
                for s, sc_type, order_idx in rows
            ]
            return edges
    
    def expand_c2e(self, character: m.Character) -> list[GraphEdge]:
        """Expand c2e (character to engagements) edges from a given character."""
        assert isinstance(character, m.Character)
        query = f"""WITH {_ctes}
            SELECT p, s, pc.summary
            FROM Engagements
            WHERE c.id = $cId
            """
        with self.__db.open_db(read_only=False) as conn:
            rows: list[tuple[pd.Series, pd.Series, str]] = conn.execute(
                query, parameters={'cId': character.id}
            ).fetchall()

            edges = [
                GraphEdge(
                    character=character,
                    person=person_row_to_model(p),
                    subject2=subject_row_to_model(s),
                    engagement_summary=summary,
                )
                for p, s, summary in rows
            ]
            return edges

    def expand_p2s(self, person: m.Person) -> list[GraphEdge]:
        """Expand p2s (person to subjects) edges from a given person."""
        assert isinstance(person, m.Person)
        query = f"""WITH {_ctes}
            SELECT s, sp.position
            FROM S2P
            WHERE p.id = $pId
            """
        with self.__db.open_db(read_only=False) as conn:
            rows: list[tuple[pd.Series, int]] = conn.execute(
                query, parameters={'pId': person.id}
            ).fetchall()

            edges = [
                GraphEdge(
                    person=person,
                    subject2=subject_row_to_model(s),
                    sp_position=m.SubjectPersonType.from_value(position),
                )
                for s, position in rows
            ]
            return edges
    
    def expand_p2e(self, person: m.Person) -> list[GraphEdge]:
        """Expand p2e (person to engagements) edges from a given person."""
        assert isinstance(person, m.Person)
        query = f"""WITH {_ctes}
            SELECT c, s, pc.summary
            FROM Engagements
            WHERE p.id = $pId
            """
        with self.__db.open_db(read_only=False) as conn:
            rows: list[tuple[pd.Series, pd.Series, str]] = conn.execute(
                query, parameters={'pId': person.id}
            ).fetchall()

            edges = [
                GraphEdge(
                    person=person,
                    character=character_row_to_model(c),
                    subject2=subject_row_to_model(s),
                    engagement_summary=summary,
                )
                for c, s, summary in rows
            ]
            return edges