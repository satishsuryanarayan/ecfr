from marshmallow import Schema, fields, post_load


class Agency:
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"


class AgencySchema(Schema):
    id = fields.String(required=True)
    name = fields.String(required=True)

    @post_load
    def make_agency(self, data: dict, **kwargs: dict) -> Agency:
        return Agency(**data)
