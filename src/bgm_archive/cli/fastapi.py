import click
from bgm_archive.duck.rdb_repo import RdbRepository
import uvicorn
from fastapi import FastAPI
from bgm_archive.api import build_app


@click.command("fastapi")
@click.option("--port", type=int, default=8000)
@click.option("--host", type=str, default="0.0.0.0")
@click.option("--duckdb", type=str, default=None)
def fastapi_server(port: int, host: str, duckdb: str):
    app = build_app(rdb=RdbRepository(duckdb))
    uvicorn.run(app, host="host", port=port)
