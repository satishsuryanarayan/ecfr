from marshmallow import Schema, fields, validates, post_load, ValidationError


class CreateCustomer:
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"


class CreateCustomerSchema(Schema):
    name = fields.Str(required=True)

    @validates("name")
    def validate_name(self, name: str, **kwargs: dict) -> None:
        if name.strip() == "":
            raise ValidationError("Customer must have a name.", fields=["name"])

    @post_load
    def make_createcustomer(self, data: dict, **kwargs: dict) -> CreateCustomer:
        return CreateCustomer(**data)
