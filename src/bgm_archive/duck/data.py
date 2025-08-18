from sys import _clear_internal_caches
from pydantic import BaseModel, Field
import bgm_archive.loader.model as m
from ihate_work.util.uniq_by import uniq_by
import logging
logger = logging.getLogger(__name__)


class GraphEdge(BaseModel):
    # edges or hyperedges in bgm_graph:
    # s for Subject, p for Person, c for Character, e for Engagement
    # directededge types: s2s
    # undirected edge types: sp / sc
    # undirected hyperedge types: scp (aka engagement)
    subject1: m.Subject | None = None
    subject2: m.Subject | None = None
    character: m.Character | None = None
    person: m.Person | None = None

    # edge properties. depending on the edge type at most 1 will be non-empty
    s2s_relation_type: m.SubjectRelationType | None = None
    sp_position: (
        m.SubjectPersonType.AnimeStuff
        | m.SubjectPersonType.BookStaff
        | m.SubjectPersonType.GameStaff
        | m.SubjectPersonType.MusicStaff
        | m.SubjectPersonType.RealStaff
        | None
    ) = None
    sc_type: m.SubjectCharacterType | None = None
    sc_order_idx: int | None = None
    engagement_summary: str | None = None


class GraphNode(m.Entity, BaseModel):
    subject: m.Subject | None = None
    character: m.Character | None = None
    person: m.Person | None = None


class GraphEdgeSimple(BaseModel):
    subject1_id: int | None = None
    subject2_id: int | None = None
    character_id: int | None = None
    person_id: int | None = None

    # edge properties. depending on the edge type at most 1 will be non-empty
    s2s_relation_type: m.SubjectRelationType | None = None
    sp_position: (
        m.SubjectPersonType.AnimeStuff
        | m.SubjectPersonType.BookStaff
        | m.SubjectPersonType.GameStaff
        | m.SubjectPersonType.MusicStaff
        | m.SubjectPersonType.RealStaff
        | None
    ) = None
    sc_type: m.SubjectCharacterType | None = None
    sc_order_idx: int | None = None
    engagement_summary: str | None = None


class Subgraph(BaseModel):
    """A subgraph around a "center" vertex"""

    center_subject: m.Subject | None = None
    center_character: m.Character | None = None
    center_person: m.Person | None = None

    subjects: list[m.Subject] = Field(default_factory=list)
    characters: list[m.Character] = Field(default_factory=list)
    persons: list[m.Person] = Field(default_factory=list)

    edges: list[GraphEdgeSimple]

    @property
    def center_str(self) -> str:
        if self.center_subject:
            return f"Subject(id={self.center_subject.id})"
        elif self.center_character:
            return f"Character(id={self.center_character.id}"
        elif self.center_person:
            return f"Person(id={self.center_person.id}"
        else:
            return "No center"

    def __add__(self, other: "Subgraph") -> "Subgraph":
        if self.center_subject and other.center_subject:
            assert self.center_subject.id == other.center_subject.id
        elif self.center_character and other.center_character:
            assert self.center_character.id == other.center_character.id
        elif self.center_person and other.center_person:
            assert self.center_person.id == other.center_person.id
        else:
            raise ValueError(
                f"Cannot add subgraphs with different centers: {self.center_str} {other.center_str}")

        return Subgraph(
            center_subject=self.center_subject,
            center_character=self.center_character,
            center_persion=self.center_person,
            subjects=uniq_by(self.subjects + other.subjects,
                             key=lambda s: s.id),
            characters=uniq_by(self.characters +
                               other.characters, key=lambda c: c.id),
            persons=uniq_by(self.persons + other.persons, key=lambda p: p.id),
            edges=self.edges + other.edges,
        ).compact()

    def compact(self) -> "Subgraph":
        """
        Returns a new Subgraph with unique subjects, characters, and persons.
        This is useful to ensure that the subgraph does not contain duplicates.
        """
        return Subgraph(
            center_subject=self.center_subject,
            center_character=self.center_character,
            center_persion=self.center_person,
            subjects=uniq_by(self.subjects, key=lambda s: s.id),
            characters=uniq_by(self.characters, key=lambda c: c.id),
            persons=uniq_by(self.persons, key=lambda p: p.id),
            edges=self.edges,
        )
