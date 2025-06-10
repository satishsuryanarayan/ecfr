from sqlalchemy import Table, Column, Integer, JSON

from api.model.database import metadata

CFR_References = Table(
    "cfr_references",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),
    Column("agency_id", Integer, nullable=False, index=True),
    Column("reference", JSON, nullable=False),
    Column("parent_agency_id", Integer, nullable=True, index=True),
)
