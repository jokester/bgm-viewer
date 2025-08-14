from .conn import DuckDbRef
import bgm_archive.loader.model as m


class DuckdbQuerier:
    def __init__(self, db_ref: DuckDbRef):
        self._db_ref = db_ref

    def find_subject_by_id(self, subject_id: int) -> m.Subject | None:
        with self._db_ref.open_db(read_only=True) as conn:
            rows = conn.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,)).fetchone()
            if not rows:
                return None
            return m.Subject.model_validate(rows)


    def find_character_by_id(self, character_id: int) -> m.Character | None:
        ...

    def find_person_by_id(self, person_id: int) -> m.Person | None:
        ...

    def find_episodes_by_subject_id(self, subject_id: int) -> list[m.Episode]:
        ...

    def find_subjects_by_ids(self, subject_ids: list[int]) -> list[m.Subject]:
        ...

    def find_characters_by_ids(self, character_ids: list[int]) -> list[m.Character]:
        ...

    def find_people_by_ids(self, person_ids: list[int]) -> list[m.Person]:
        ...
