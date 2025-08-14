from pathlib import Path
import duckdb
import contextlib
from typing import ContextManager, Union

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DuckDbRef:
    def __init__(self, path: Union[str, Path]):
        self.__path = Path(path)

    @classmethod
    def from_db(cls, db: Union[str, Path, 'DuckDbRef']) -> 'DuckDbRef':
        """Create a DuckDbRef from various database reference types"""
        if isinstance(db, cls):
            return db
        return cls(db)

    def open_db(self, read_only=False) -> ContextManager['duckdb.DuckDBPyConnection']:
        @contextlib.contextmanager
        def create():
            db = duckdb.connect(self.__path, read_only=read_only)
            db.load_extension("duckpgq")
            yield db  # type: ignore
            db.close()

        return create()
