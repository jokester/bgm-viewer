from pydantic import BaseModel
import bgm_archive.loader.model as m


class Subgraph(BaseModel):
    """A subgraph of vertices/edges around to a "from" vertex"""
    from_subject: m.Subject | None = None
    from_character: m.Character | None = None
    from_person: m.Person | None = None

    edges: list['GraphEdge']


class GraphEdge(BaseModel):
    to_subject: m.Subject | None = None
    to_character: m.Character | None = None
    to_person: m.Person | None = None

    to_occ: 'PersonOccurance | None' = None

    s2s_relation_type: m.SubjectRelationType | None = None
    p2c_summary: str | None = None
    s2p_position: m.SubjectPersonType.AnimeStuff | m.SubjectPersonType.BookStaff | m.SubjectPersonType.GameStaff | m.SubjectPersonType.MusicStaff | m.SubjectPersonType.RealStaff | None = None
    s2c_type: m.SubjectCharacterType | None = None


class GraphNode(m.Entity, BaseModel):
    subject: m.Subject | None = None
    character: m.Character | None = None
    person: m.Person | None = None


class PersonOccurance(BaseModel):
    subject: m.Subject | None = None
    character: m.Character | None = None
    person: m.Person | None = None
    summary: str | None = None
