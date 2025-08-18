import bgm_archive.loader.model as m
from .conn import DuckDbRef
from pathlib import Path
from .data import GraphEdge, Subgraph, GraphEdgeSimple
from .rdb_repo import person_row_to_model, subject_row_to_model, character_row_to_model
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
    """Provide "graph expansion" methods to query a graph. A expand_* call returns a Subgraph"""

    def __init__(self, db: DuckDbRef | str | Path):
        self.__db = DuckDbRef.from_db(db)

    def expand_s2s(self, from_subject: m.Subject) -> Subgraph:
        """Expand s2s (subject to subject) edges from a given subject."""
        assert isinstance(from_subject, m.Subject)
        query = f"""WITH {_ctes}
            SELECT s2, sr.relation_type
            FROM S2S
            WHERE s1.id = $sId
            """
        with self.__db.open_db(read_only=False) as conn:
            rows: list[tuple[dict, int]] = conn.execute(
                query, parameters={"sId": from_subject.id}
            ).fetchall()

            edges = [
                GraphEdgeSimple(
                    subject1_id=from_subject.id,
                    subject2_id=subject_row_to_model(s2).id,
                    s2s_relation_type=m.SubjectRelationType(subject_relation_type),
                )
                for s2, subject_relation_type in rows
            ]

            # Extract unique subjects from edges
            subjects = [from_subject] + [subject_row_to_model(s2) for s2, _ in rows]

            return Subgraph(subjects=subjects, edges=edges)

    def expand_sp(self, subject1: m.Subject) -> Subgraph:
        """Expand s2p (subject to persons) edges from a given subject."""
        assert isinstance(subject1, m.Subject)
        query = f"""WITH {_ctes}
            SELECT p, sp.position
            FROM S2P
            WHERE s.id = $sId
            """
        with self.__db.open_db(read_only=False) as conn:
            rows: list[tuple[pd.Series, int]] = conn.execute(
                query, parameters={"sId": subject1.id}
            ).fetchall()

            edges = [
                GraphEdgeSimple(
                    subject1_id=subject1.id,
                    person_id=person_row_to_model(p).id,
                    sp_position=m.SubjectPersonType.from_value(position),
                )
                for p, position in rows
            ]

            # Extract unique persons from edges
            persons = [person_row_to_model(p) for p, _ in rows]

            return Subgraph(subjects=[subject1], persons=persons, edges=edges)

    def expand_sc(self, subject: m.Subject) -> Subgraph:
        """Expand s2c (subject to characters) edges from a given subject."""
        assert isinstance(subject, m.Subject)
        query = f"""WITH {_ctes}
            SELECT c, sc.type, sc.order_idx
            FROM S2C
            WHERE s.id = $sId
            """
        with self.__db.open_db(read_only=False) as conn:
            rows: list[tuple[pd.Series, int, int]] = conn.execute(
                query, parameters={"sId": subject.id}
            ).fetchall()

            edges = [
                GraphEdgeSimple(
                    subject1_id=subject.id,
                    character_id=character_row_to_model(c).id,
                    sc_type=m.SubjectCharacterType(sc_type),
                    sc_order_idx=order_idx,
                )
                for c, sc_type, order_idx in rows
            ]

            # Extract unique characters from edges
            characters = [character_row_to_model(c) for c, _, _ in rows]

            return Subgraph(subjects=[subject], characters=characters, edges=edges)

    def expand_se(self, subject: m.Subject) -> Subgraph:
        """Expand s2e (subject to engagements) edges from a given subject."""
        assert isinstance(subject, m.Subject)
        query = f"""WITH {_ctes}
            SELECT p, c, pc.summary
            FROM Engagements
            WHERE s.id = $sId
            """
        with self.__db.open_db(read_only=False) as conn:
            rows: list[tuple[pd.Series, pd.Series, str]] = conn.execute(
                query, parameters={"sId": subject.id}
            ).fetchall()

            edges = [
                GraphEdgeSimple(
                    subject1_id=subject.id,
                    person_id=person_row_to_model(p).id,
                    character_id=character_row_to_model(c).id,
                    engagement_summary=summary,
                )
                for p, c, summary in rows
            ]

            # Extract unique persons and characters from edges
            persons = [person_row_to_model(p) for p, _, _ in rows]
            characters = [character_row_to_model(c) for _, c, _ in rows]

            return Subgraph(
                subjects=[subject], persons=persons, characters=characters, edges=edges
            )

    def expand_cs(self, character: m.Character) -> Subgraph:
        """Expand c2s (character to subjects) edges from a given character."""
        assert isinstance(character, m.Character)
        query = f"""WITH {_ctes}
            SELECT s, sc.type, sc.order_idx
            FROM S2C
            WHERE c.id = $cId
            """
        with self.__db.open_db(read_only=False) as conn:
            rows: list[tuple[pd.Series, int, int]] = conn.execute(
                query, parameters={"cId": character.id}
            ).fetchall()

            edges = [
                GraphEdgeSimple(
                    character_id=character.id,
                    subject2_id=subject_row_to_model(s).id,
                    sc_type=m.SubjectCharacterType(sc_type),
                    sc_order_idx=order_idx,
                )
                for s, sc_type, order_idx in rows
            ]

            # Extract unique subjects from edges
            subjects = [subject_row_to_model(s) for s, _, _ in rows]

            return Subgraph(subjects=subjects, characters=[character], edges=edges)

    def expand_ce(self, character: m.Character) -> Subgraph:
        """Expand c2e (character to engagements) edges from a given character."""
        assert isinstance(character, m.Character)
        query = f"""WITH {_ctes}
            SELECT p, s, pc.summary
            FROM Engagements
            WHERE c.id = $cId
            """
        with self.__db.open_db(read_only=False) as conn:
            rows: list[tuple[pd.Series, pd.Series, str]] = conn.execute(
                query, parameters={"cId": character.id}
            ).fetchall()

            edges = [
                GraphEdgeSimple(
                    character_id=character.id,
                    person_id=person_row_to_model(p).id,
                    subject2_id=subject_row_to_model(s).id,
                    engagement_summary=summary,
                )
                for p, s, summary in rows
            ]

            # Extract unique persons and subjects from edges
            persons = [person_row_to_model(p) for p, _, _ in rows]
            subjects = [subject_row_to_model(s) for _, s, _ in rows]

            return Subgraph(
                subjects=subjects, characters=[character], persons=persons, edges=edges
            )

    def expand_ps(self, person: m.Person) -> Subgraph:
        """Expand p2s (person to subjects) edges from a given person."""
        assert isinstance(person, m.Person)
        query = f"""WITH {_ctes}
            SELECT s, sp.position
            FROM S2P
            WHERE p.id = $pId
            """
        with self.__db.open_db(read_only=False) as conn:
            rows: list[tuple[pd.Series, int]] = conn.execute(
                query, parameters={"pId": person.id}
            ).fetchall()

            edges = [
                GraphEdgeSimple(
                    person_id=person.id,
                    subject2_id=subject_row_to_model(s).id,
                    sp_position=m.SubjectPersonType.from_value(position),
                )
                for s, position in rows
            ]

            # Extract unique subjects from edges
            subjects = [subject_row_to_model(s) for s, _ in rows]

            return Subgraph(subjects=subjects, persons=[person], edges=edges)

    def expand_pe(self, person: m.Person) -> Subgraph:
        """Expand p2e (person to engagements) edges from a given person."""
        assert isinstance(person, m.Person)
        query = f"""WITH {_ctes}
            SELECT c, s, pc.summary
            FROM Engagements
            WHERE p.id = $pId
            """
        with self.__db.open_db(read_only=False) as conn:
            rows: list[tuple[pd.Series, pd.Series, str]] = conn.execute(
                query, parameters={"pId": person.id}
            ).fetchall()

            edges = [
                GraphEdgeSimple(
                    person_id=person.id,
                    character_id=character_row_to_model(c).id,
                    subject2_id=subject_row_to_model(s).id,
                    engagement_summary=summary,
                )
                for c, s, summary in rows
            ]

            # Extract unique characters and subjects from edges
            characters = [character_row_to_model(c) for c, _, _ in rows]
            subjects = [subject_row_to_model(s) for _, s, _ in rows]

            return Subgraph(
                subjects=subjects, characters=characters, persons=[person], edges=edges
            )
