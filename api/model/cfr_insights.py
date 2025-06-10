from sqlalchemy import Table, Column, Integer, Date, String

from api.model.database import metadata

CFR_Insights = Table(
    "cfr_insights",
    metadata,
    Column("cfr_reference_id", Integer, nullable=False, index=True),
    Column("agency_id", Integer, nullable=False, index=True),
    Column("parent_agency_id", Integer, nullable=True, index=True),
    Column("date", Date, nullable=False, index=True),
    Column("word_count", Integer, nullable=False),
    Column("checksum", String(256), nullable=False),
    Column("restrictive_terms_count", Integer, nullable=False),
)
