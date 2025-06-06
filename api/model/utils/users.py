from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import LargeBinary, String

from bank.model.metadata import metadata

Users = Table(
    "users",
    metadata,
    Column("username", String(20), primary_key=True, nullable=False, index=True),
    Column("password", LargeBinary, nullable=False),
    Column("email", String(120), nullable=False)
)
