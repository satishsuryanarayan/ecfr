from sqlalchemy import Table, Column, Integer
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DECIMAL, DateTime, BigInteger

from bank.model.metadata import metadata

Transfers = Table(
    "transfers",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True, nullable=False),
    Column("from_account_id", Integer, ForeignKey("accounts.id"), nullable=False, index=True),
    Column("to_account_id", Integer, ForeignKey("accounts.id"), nullable=False, index=True),
    Column("amount", DECIMAL(15, 2), nullable=False),
    Column("time", DateTime, default=func.now(), onupdate=func.now(), nullable=False, index=True)
)
