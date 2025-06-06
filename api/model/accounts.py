from sqlalchemy import Table, Column, Integer
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime

from bank.model.metadata import metadata

Accounts = Table(
    "accounts",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),
    Column("customer_id", Integer, ForeignKey("customers.id"), nullable=False, index=True),
    Column("creation_time", DateTime, default=func.now(), nullable=False, index=True)
)
