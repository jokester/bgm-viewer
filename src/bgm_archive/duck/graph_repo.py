import bgm_archive.loader.model as m
from .conn import DuckDbRef
from pathlib import Path
from .data import GraphEdge, GraphNode
from .rdb_repo import RdbRepository


class GraphRepository:
    def __init__(self, db: DuckDbRef | str | Path, rdb: RdbRepository):
        self.__db = DuckDbRef.from_db(db)
        self.__rdb = rdb

    def expand_s2e(self, subject_id: int) -> GraphEdge: ...
