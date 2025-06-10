from sqlalchemy import Table, Column, Integer, JSON
from sqlalchemy.sql.schema import ForeignKey

from api.model.database import metadata

CFR_References = Table(
    "cfr_references",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),
    Column("agency_id", Integer, ForeignKey("agencies.id"), nullable=False, index=True),
    Column("reference", JSON, nullable=False),
    Column("parent_agency_id", Integer, ForeignKey("agencies.id"), nullable=True, index=True),
)
