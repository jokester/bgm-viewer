from pathlib import Path
import duckdb


class BgmDb():
    def __init__(self, path: str | Path, read_only: bool = True):
        self.__db = duckdb.connect(str(path), read_only=read_only)

    def setup_db(self):
        pass
