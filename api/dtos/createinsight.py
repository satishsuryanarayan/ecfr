from datetime import datetime
from marshmallow import Schema, fields, post_load


class CreateInsight:
    def __init__(self, agency_id: int, date: datetime) -> None:
        self.agency_id = agency_id
        self.date = date

    def __repr__(self):
        return f"{self.__class__.__name__}(agency_id={self.agency_id}, date={self.date})"


class CreateInsightSchema(Schema):
    agency_id = fields.Integer(required=True)
    date = fields.Date(required=True)

    @post_load
    def make_create_insight(self, data: dict, **kwargs: dict) -> CreateInsight:
        return CreateInsight(**data)
