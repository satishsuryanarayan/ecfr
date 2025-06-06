from datetime import datetime

from marshmallow import Schema, fields, post_load

class FromToQuery:
    def __init__(self, from_time: datetime, to_time: datetime) -> None:
        self.from_time = from_time
        self.to_time = to_time

    def __repr__(self):
        return f"{self.__class__.__name__}(from_time={self.from_time}, to_time={self.to_time})"

class FromToQuerySchema(Schema):
    from_time = fields.DateTime(required=False)
    to_time = fields.DateTime(required=False)

    @post_load
    def make_fromtoquery(self, data: dict, **kwargs: dict) -> FromToQuery:
        if "from_time" not in data:
            data["from_time"] = None
        if "to_time" not in data:
            data["to_time"] = None
        return FromToQuery(**data)

