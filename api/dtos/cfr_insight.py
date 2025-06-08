from datetime import datetime

from marshmallow import Schema, fields, post_load


class CFRInsight:
    def __init__(self, cfr_reference_id: int, agency_id: int, parent_agency_id: int, date: datetime, checksum: str, word_count: str,
                 restrictive_terms_count: str) -> None:
        self.cfr_reference_id = cfr_reference_id
        self.agency_id = agency_id
        self.parent_agency_id = parent_agency_id
        self.date = date
        self.checksun = checksum
        self.word_count = word_count
        self.restrictive_terms_count = restrictive_terms_count

    def __repr__(self):
        return f"{self.__class__.__name__}(cfr_reference_id={self.cfr_reference_id}, agency_id={self.agency_id}, parent_agency_id={self.parent_agency_id}, date={self.date}, checksum={self.checksun}, word_count={self.word_count}, restricted_word_count={self.restrictive_terms_count})"


class CFRInsightSchema(Schema):
    cfr_reference_id = fields.Integer(required=True)
    agency_id = fields.Integer(required=True)
    parent_agency_id = fields.Integer(required=False, allow_none=True)
    date = fields.Date(required=True)
    checksum = fields.Str(required=True)
    word_count = fields.Integer(required=True)
    restrictive_terms_count = fields.Integer(required=True)

    @post_load
    def make_cfr_insight(self, data: dict, **kwargs: dict) -> CFRInsight:
        return CFRInsight(**data)
