from sqlalchemy import Table, Column, Integer
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DECIMAL, DateTime

from api.model.metadata import metadata

Balances = Table(
    "balances",
    metadata,
    Column("account_id", Integer, ForeignKey("accounts.id"), nullable=False, index=True),
    Column("amount", DECIMAL(15, 2), nullable=False),
    Column("last_updated_time", DateTime, default=func.now(), onupdate=func.now(), nullable=False)
)
