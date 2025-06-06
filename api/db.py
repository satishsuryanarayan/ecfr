import click
from flask import current_app, g
from sqlalchemy.engine import Connection
from sqlalchemy.exc import TimeoutError
from typing_extensions import Literal

from api.model.metadata import metadata

IsolationLevel = Literal["REPEATABLE READ", "SERIALIZABLE"]


# Add the database connection to the application context and the return it
def get_connection(isolation_level: IsolationLevel = "SERIALIZABLE") -> Connection:
    if "connections" not in g:
        g.connections = dict()
        g.connections[isolation_level] = current_app.config[isolation_level].connect()

    if isolation_level not in g.connections:
        g.connections[isolation_level] = current_app.config[isolation_level].connect()

    return g.connections[isolation_level]


# Get the database connection from the application context and close it
def close_connection(e=None):
    connections: dict = g.pop("connections", None)
    if connections is not None:
        if "SERIALIZABLE" in connections:
            connections["SERIALIZABLE"].close()
        if "REPEATABLE READ" in connections:
            connections["REPEATABLE READ"].close()


# Initialize the database
def init_db():
    try:
        connection: Connection = get_connection(isolation_level="SERIALIZABLE")
    except TimeoutError as pe:
        current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
        return

    try:
        with connection.begin():
            metadata.drop_all(bind=connection)
            metadata.create_all(bind=connection)
    except Exception as e:
        current_app.logger.error("Error during database initialization: %s", e, exc_info=True)


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_connection)
    app.cli.add_command(init_db_command)
