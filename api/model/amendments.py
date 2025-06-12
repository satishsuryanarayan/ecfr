from sqlalchemy import Table, Column, Integer, ForeignKey, Date

from api.model.database import metadata
from api.model.titles import Titles

Amendments = Table(
    "amendments",
    metadata,
    Column("title", Integer, ForeignKey(Titles.c.number), nullable=False, index=True),
    Column("amendment_date", Date, nullable=False),
    Column("issue_date", Date, nullable=False),
)
