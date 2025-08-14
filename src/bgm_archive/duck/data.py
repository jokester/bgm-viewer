from pydantic import BaseModel
import bgm_archive.loader.model as m


# a union type for all possible
class GraphEdge(BaseModel):
    from_subject: m.Subject | None = None
    from_character: m.Character | None = None
    from_person: m.Person | None = None

    to_subject: m.Subject | None = None
    to_character: m.Character | None = None
    to_person: m.Person | None = None

    s2s_relation_type: m.SubjectRelationType | None = None
    p2c_summary: m.SubjectPerson | None = None
    s2p_position: m.SubjectPersonType | None = None
    s2c_type: m.SubjectCharacterType | None = None


class GraphNode(m.Entity, BaseModel):
    subject: m.Subject | None = None
    character: m.Character | None = None
    person: m.Person | None = None
