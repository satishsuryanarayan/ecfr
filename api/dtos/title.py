from typing import List

from marshmallow import Schema, fields, post_load

from api.dtos.amendment import AmendmentSchema, Amendment


class Title:
    def __init__(self, number: int, name: str, amendments: List[Amendment]) -> None:
        self.number = number
        self.name = name
        self.amendments = amendments

    def __repr__(self):
        return f"{self.__class__.__name__}(number={self.number}, name={self.name}, amendments={self.amendments})"


class TitleSchema(Schema):
    number = fields.Integer(required=True)
    name = fields.String(required=True)
    amendments = fields.Nested(AmendmentSchema(many=True), required=True)

    @post_load
    def make_title(self, data: dict, **kwargs: dict) -> Title:
        return Title(**data)
