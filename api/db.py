from flask import current_app, g
from sqlalchemy.engine import Connection
from typing_extensions import Literal

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
def close_connection():
    connections: dict = g.pop("connections", None)
    if connections is not None:
        if "SERIALIZABLE" in connections:
            connections["SERIALIZABLE"].close()
        if "REPEATABLE READ" in connections:
            connections["REPEATABLE READ"].close()


def init_app(app):
    app.teardown_appcontext(close_connection)
