from pydantic import BaseModel
import bgm_archive.loader.model as m


class GraphEdge(BaseModel):
    # edges or hyperedges in bgm_graph:
    # s for Subject, p for Person, c for Character, e for Engagement
    # directededge types: s2s
    # undirected edge types: sp / sc
    # hyperedge types: scp (aka engagement)
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

class Subgraph(BaseModel):
    """A subgraph around a "center" vertex"""

    center: GraphNode
    edges: list[GraphEdge]

