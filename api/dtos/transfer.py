import datetime
import decimal

from marshmallow import Schema, fields, post_load


class Transfer:
    def __init__(self, id: int, from_account_id: int, to_account_id: int, amount: decimal, time: datetime) -> None:
        self.id = id
        self.from_account_id = from_account_id
        self.to_account_id = to_account_id
        self.amount = amount
        self.time = time

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, from_account_id={self.from_account_id}, to_account_id={self.to_account_id}, amount={self.amount}, time={self.time})"


class TransferSchema(Schema):
    id = fields.Int(required=True)
    from_account_id = fields.Int(required=True)
    to_account_id = fields.Int(required=True)
    amount = fields.Decimal(required=True, as_string=True)
    time = fields.DateTime(required=True)

    @post_load
    def make_transfer(self, data: dict, **kwargs: dict) -> Transfer:
        return Transfer(**data)
