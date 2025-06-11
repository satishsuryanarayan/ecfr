from flask import current_app
from sqlalchemy import Connection

from api.db import get_connection
from api.model.database import metadata


class DatabaseController:
    @classmethod
    def initialize(cls, force: bool = False) -> None:
        current_app.logger.debug("Initializing database...")
        try:
            connection: Connection = get_connection(isolation_level="SERIALIZABLE")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            with connection.begin():
                if force:
                    metadata.drop_all(connection)
                metadata.create_all(connection)
            current_app.logger.info("Database initialized.")
        except Exception as e:
            current_app.logger.error("Exception while creating database tables: %s", e, exc_info=True)
            raise e
