from datetime import datetime

from marshmallow import Schema, fields, post_load


class FromToQuery:
    def __init__(self, from_date: datetime, to_date: datetime) -> None:
        self.from_date = from_date
        self.to_date = to_date

    def __repr__(self):
        return f"{self.__class__.__name__}(from_date={self.from_date}, to_date={self.to_date})"


class FromToQuerySchema(Schema):
    from_date = fields.Date(required=False)
    to_date = fields.Date(required=False)

    @post_load
    def make_from_to_query(self, data: dict, **kwargs: dict) -> FromToQuery:
        if "from_date" not in data:
            data["from_date"] = None
        if "to_date" not in data:
            data["to_date"] = None
        return FromToQuery(**data)
