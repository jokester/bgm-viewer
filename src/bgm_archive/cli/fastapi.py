import click
from fastapi import FastAPI


def build_fastapi_app() -> FastAPI:
    """Build and return the FastAPI application."""
    from bgm_archive.api import fastapi

    return fastapi


@click.command('fastapi')
def fastapi_server():
    # TODO
    pass
