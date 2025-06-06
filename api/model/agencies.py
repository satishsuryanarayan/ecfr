from sqlalchemy import Table, Column, String, ForeignKey, Integer

from api.model.metadata import metadata

Agencies = Table(
    "agencies",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),
    Column("short_name", String(256) , nullable=True),
    Column("name", String(512), nullable=False),
    Column("parent_id", Integer, ForeignKey("agencies.id"), nullable=True, index=True),
)
