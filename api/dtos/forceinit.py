from marshmallow import Schema, fields, post_load


class ForceInit:
    def __init__(self, flag: bool) -> None:
        self.flag = flag

    def __repr__(self):
        return f"{self.__class__.__name__}(force_init={self.flag})"


class ForceInitSchema(Schema):
    flag = fields.Boolean(required=True)

    @post_load
    def make_force_init(self, data: dict, **kwargs: dict) -> ForceInit:
        return ForceInit(**data)
