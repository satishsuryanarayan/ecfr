from sqlalchemy import Table, Column, String, Integer

from api.model.database import metadata

Titles = Table(
    "titles",
    metadata,
    Column("number", Integer, primary_key=True, autoincrement=False, nullable=False),
    Column("name", String(256), nullable=False),
)
