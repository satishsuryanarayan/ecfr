from datetime import datetime

from marshmallow import Schema, fields, post_load


class AmendmentDate:
    def __init__(self, amendment_date: datetime) -> None:
        self.amendment_date = amendment_date

    def __repr__(self):
        return f"{self.__class__.__name__}(amendment_date={self.amendment_date})"


class AmendmentDateSchema(Schema):
    amendment_date = fields.Date(format="%Y-%m-%d", required=True)

    @post_load
    def make_amendment_date(self, data: dict, **kwargs: dict) -> AmendmentDate:
        return AmendmentDate(**data)
