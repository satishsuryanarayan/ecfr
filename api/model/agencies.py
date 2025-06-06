from sqlalchemy import Table, Column, Integer, String, ForeignKey

from api.model.metadata import metadata

Agencies = Table(
    "agencies",
    metadata,
    Column("id", String(10), primary_key=True, nullable=False),
    Column("name", String(256), nullable=False, index=True),
    Column("parent_id", String(10), ForeignKey("agencies.id"), nullable=True, index=True),
)
