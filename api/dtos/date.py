from datetime import datetime

from marshmallow import Schema, fields, post_load


class Date:
    def __init__(self, date: datetime) -> None:
        self.date = date

    def __repr__(self):
        return f"{self.__class__.__name__}(date={self.date})"


class DateSchema(Schema):
    date = fields.Date(format="%Y-%m-%d", required=True)

    @post_load
    def make_issue_date(self, data: dict, **kwargs: dict) -> Date:
        return Date(**data)
