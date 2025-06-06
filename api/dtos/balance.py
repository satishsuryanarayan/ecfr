import decimal
from datetime import datetime

from marshmallow import Schema, fields, post_load


class Balance:
    def __init__(self, account_id: int, amount: decimal, last_updated_time: datetime) -> None:
        self.account_id = account_id
        self.amount = amount
        self.last_updated_time = last_updated_time

    def __repr__(self):
        return f"{self.__class__.__name__}(account_id={self.account_id}, amount={self.amount}, last_updated_time={self.last_updated_time})"


class BalanceSchema(Schema):
    account_id = fields.Int(required=True)
    amount = fields.Decimal(required=True, as_string=True)
    last_updated_time = fields.DateTime(required=True)

    @post_load
    def make_balance(self, data: dict, **kwargs: dict) -> Balance:
        return Balance(**data)
