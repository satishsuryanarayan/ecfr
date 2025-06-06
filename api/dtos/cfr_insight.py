from datetime import datetime
from marshmallow import Schema, fields, post_load


class CFRInsight:
    def __init__(self, cfr_reference_id: int, agency_id: str, parent_agency_id: str, date: datetime, word_count: str, restricted_word_count: str) -> None:
        self.cfr_reference_id = cfr_reference_id
        self.parent_agency_id = parent_agency_id
        self.agency_id = agency_id
        self.date = date
        self.word_count = word_count
        self.restricted_word_count = restricted_word_count

    def __repr__(self):
        return f"{self.__class__.__name__}(cfr_reference_id={self.cfr_reference_id}, agency_id={self.agency_id}, parent_agency_id={self.parent_agency_id}, date={self.date}, word_count={self.word_count}, restricted_word_count={self.restricted_word_count})"


class CFRInsightSchema(Schema):
    cfr_reference_id = fields.Integer(required=True)
    agency_id = fields.String(required=True)
    parent_agency_id = fields.String(required=False, allow_none=True)
    date = fields.Date(required=True)
    word_count = fields.Integer(required=True)
    restricted_word_count = fields.Integer(required=True)

    @post_load
    def make_cfr_insight(self, data: dict, **kwargs: dict) -> CFRInsight:
        return CFRInsight(**data)