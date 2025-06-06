from datetime import datetime

from marshmallow import Schema, fields, post_load


class Customer:
    def __init__(self, id: int, name: str, creation_time: datetime) -> None:
        self.id = id
        self.name = name
        self.creation_time = creation_time

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name}, creation_time={self.creation_time})"


class CustomerSchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True)
    creation_time = fields.DateTime(required=True)

    @post_load
    def make_customer(self, data: dict, **kwargs: dict) -> Customer:
        return Customer(**data)
