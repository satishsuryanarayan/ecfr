from datetime import datetime

from marshmallow import Schema, fields, post_load


class Amendment:
    def __init__(self, title: int, amendment_date: datetime, issue_date: datetime) -> None:
        self.title = title
        self.amendment_date = amendment_date
        self.issue_date = issue_date

    def __repr__(self):
        return f"{self.__class__.__name__}(title={self.title}, amendment_date={self.amendment_date}, issue_date={self.issue_date})"


class AmendmentSchema(Schema):
    title = fields.Integer(required=True)
    amendment_date = fields.Date(required=True)
    issue_date = fields.Date(required=True)

    @post_load
    def make_amendment(self, data: dict, **kwargs: dict) -> Amendment:
        return Amendment(**data)
