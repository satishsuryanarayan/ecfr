import decimal
from decimal import Decimal

from marshmallow import Schema, fields, validates, post_load, ValidationError


class CreateAccount:
    def __init__(self, customer_id: int, amount: decimal) -> None:
        self.customer_id = customer_id
        self.amount = amount

    def __repr__(self):
        return f"{self.__class__.__name__}(customer_id={self.customer_id}, amount={self.amount})"


class CreateAccountSchema(Schema):
    customer_id = fields.Int(required=True)
    amount = fields.Decimal(required=True)

    @validates("amount")
    def validate_amount(self, amount: Decimal, **kwargs: dict) -> None:
        if amount <= 0:
            raise ValidationError("Balance must be greater than zero.", fields=["amount"])

    @post_load
    def make_createaccount(self, data: dict, **kwargs: dict) -> CreateAccount:
        return CreateAccount(**data)
