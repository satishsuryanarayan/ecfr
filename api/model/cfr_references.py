from sqlalchemy import Table, Column, Integer, JSON, event, DDL

from api.model.database import metadata

CFR_References = Table(
    "cfr_references",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),
    Column("agency_id", Integer, nullable=False, index=True),
    Column("reference", JSON, nullable=False),
    Column("parent_agency_id", Integer, nullable=True, index=True),
)

event.listen(
    metadata,
    "after_create",
    DDL(
        "ALTER TABLE cfr_references PARTITION BY HASH(agency_id) PARTITIONS 350;"
    ),
)
