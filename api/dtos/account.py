from datetime import datetime

from marshmallow import Schema, fields, post_load


class Account:
    def __init__(self, id: int, customer_id: int, creation_time: datetime) -> None:
        self.id = id
        self.customer_id = customer_id
        self.creation_time = creation_time

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, customer_id={self.customer_id}, creation_time={self.creation_time})"


class AccountSchema(Schema):
    id = fields.Int(required=True)
    customer_id = fields.Int(required=True)
    creation_time = fields.DateTime(required=True)

    @post_load
    def make_account(self, data: dict, **kwargs: dict) -> Account:
        return Account(**data)
