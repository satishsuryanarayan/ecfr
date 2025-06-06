import decimal
from decimal import Decimal

from marshmallow import Schema, fields, validates, validates_schema, post_load, ValidationError


class CreateTransfer:
    def __init__(self, from_account_id: int, to_account_id: int, amount: decimal) -> None:
        self.from_account_id = from_account_id
        self.to_account_id = to_account_id
        self.amount = amount

    def __repr__(self):
        return f"{self.__class__.__name__}(from_account_id={self.from_account_id}, to_account_id={self.to_account_id}, amount={self.amount})"


class CreateTransferSchema(Schema):
    from_account_id = fields.Int(required=True)
    to_account_id = fields.Int(required=True)
    amount = fields.Decimal(required=True, as_string=True)

    @validates("amount")
    def validate_amount(self, amount: Decimal, **kwargs: dict) -> None:
        if amount < 0:
            raise ValidationError("Transfer amount cannot be negative.", fields=["amount"])

    @validates_schema
    def validate_from_and_to_account_ids(self, data: dict, **kwargs: dict) -> None:
        if data["from_account_id"] == data["to_account_id"]:
            raise ValidationError("Cannot transfer money to same account.")

    @post_load
    def make_createtransfer(self, data: dict, **kwargs: dict) -> CreateTransfer:
        return CreateTransfer(**data)
