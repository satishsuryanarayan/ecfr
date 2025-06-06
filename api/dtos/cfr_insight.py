from datetime import datetime
from marshmallow import Schema, fields, post_load


class CFRInsight:
    def __init__(self, cfr_reference_id: int, date: datetime, word_count: str, restrictive_terms_count: str) -> None:
        self.cfr_reference_id = cfr_reference_id
        self.date = date
        self.word_count = word_count
        self.restrictive_terms_count = restrictive_terms_count

    def __repr__(self):
        return f"{self.__class__.__name__}(cfr_reference_id={self.cfr_reference_id}, date={self.date}, word_count={self.word_count}, restricted_word_count={self.restrictive_terms_count})"


class CFRInsightSchema(Schema):
    cfr_reference_id = fields.Integer(required=True)
    date = fields.Date(required=True)
    word_count = fields.Integer(required=True)
    restrictive_terms_count = fields.Integer(required=True)

    @post_load
    def make_cfr_insight(self, data: dict, **kwargs: dict) -> CFRInsight:
        return CFRInsight(**data)