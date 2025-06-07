from sqlalchemy import Table, Column, Integer, Date
from sqlalchemy.sql.schema import ForeignKey

from api.model.metadata import metadata

CFR_Insights = Table(
    "cfr_insights",
    metadata,
    Column("cfr_reference_id", Integer, ForeignKey("cfr_references.id"), nullable=False, index=True),
    Column("agency_id", Integer, ForeignKey("agencies.id"), nullable=False, index=True),
    Column("parent_agency_id", Integer, ForeignKey("agencies.id"), nullable=True, index=True),
    Column("date", Date, nullable=False, index=True),
    Column("word_count", Integer, nullable=False),
    Column("restrictive_terms_count", Integer, nullable=False),
)
