from marshmallow import Schema, fields, post_load


class Agency:
    def __init__(self, id: int, short_name: str, name: str, parent_id: int) -> None:
        self.id = id
        self.short_name = short_name
        self.name = name
        self.parent_id = parent_id

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, short_name={self.short_name}, name={self.name}, parent_id={self.parent_id})"


class AgencySchema(Schema):
    id = fields.Integer(required=True)
    short_name = fields.String(required=False, allow_none=True)
    name = fields.String(required=True)
    parent_id = fields.Integer(required=False, allow_none=True)

    @post_load
    def make_agency(self, data: dict, **kwargs: dict) -> Agency:
        return Agency(**data)
