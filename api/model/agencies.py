from sqlalchemy import Table, Column, String, ForeignKey, Integer, event, DDL

from api.model.database import metadata

Agencies = Table(
    "agencies",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),
    Column("short_name", String(256), nullable=True),
    Column("name", String(512), nullable=False),
    Column("parent_id", Integer, ForeignKey("agencies.id"), nullable=True, index=True),
)

event.listen(
    metadata,
    "after_create",
    DDL(
        "ALTER TABLE agencies PARTITION BY HASH(id) PARTITIONS 350;"
    ),
)
