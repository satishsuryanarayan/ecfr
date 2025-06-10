from sqlalchemy import Table, Column, String, Integer, event, DDL

from api.model.database import metadata

Agencies = Table(
    "agencies",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),
    Column("short_name", String(256), nullable=True),
    Column("name", String(512), nullable=False),
    Column("parent_id", Integer, nullable=True, index=True),
)

event.listen(
    Agencies,
    "after_create",
    DDL(
        "ALTER TABLE agencies PARTITION BY KEY() PARTITIONS 350;"
    ),
)
