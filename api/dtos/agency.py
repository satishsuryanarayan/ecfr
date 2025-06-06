from marshmallow import Schema, fields, post_load


class Agency:
    def __init__(self, id: str, name: str, parent_id: str) -> None:
        self.id = id
        self.name = name
        self.parent_id = parent_id

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name}, parent_id={self.parent_id})"


class AgencySchema(Schema):
    id = fields.String(required=True)
    name = fields.String(required=True)
    parent_id = fields.String(required=False, allow_none=True)

    @post_load
    def make_agency(self, data: dict, **kwargs: dict) -> Agency:
        return Agency(**data)
