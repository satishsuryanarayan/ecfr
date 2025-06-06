from sqlalchemy import Table, Column, Integer, JSON, Boolean, String
from sqlalchemy.sql.schema import ForeignKey

from api.model.metadata import metadata

CFR_References = Table(
    "cfr_reference_insights",
    metadata,
Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),
    Column("agency_id", String, ForeignKey("agencies.id"), nullable=False, index=True),
    Column("reference", JSON, nullable=False),
    Column("parent_agency_id", String, ForeignKey("agencies.id"), nullable=True, index=True),
)
