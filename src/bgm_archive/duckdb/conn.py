import duckdb
from pathlib import Path
import contextlib
from typing import ContextManager

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DuckDbRef:
    def __init__(self, path: str | Path):
        self._path = Path(path)

    def open_db(self, read_only=False) -> ContextManager[duckdb.DuckDBPyConnection]:
        @contextlib.contextmanager
        def create():
            db = duckdb.connect(self._path, read_only=read_only)
            db.load_extension("duckpgq")
            yield db  # type: ignore
            self._conn = None  # type: ignore
            db.close()

        return create()
