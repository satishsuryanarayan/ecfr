from sqlalchemy import MetaData, event, DDL

metadata: MetaData = MetaData()

event.listen(
    metadata,
    "after_create",
    DDL(
        "ALTER TABLE agencies PARTITION BY KEY() PARTITIONS 350;"
        "ALTER TABLE cfr_insights PARTITION BY HASH(agency_id) PARTITIONS 350;"
        "ALTER TABLE cfr_references PARTITION BY HASH(agency_id) PARTITIONS 350;"
    ),
)
