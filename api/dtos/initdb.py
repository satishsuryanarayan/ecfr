from marshmallow import Schema, fields, post_load


class InitDB:
    def __init__(self, force: bool) -> None:
        self.force = force

    def __repr__(self):
        return f"{self.__class__.__name__}(force_init={self.force})"


class InitDBSchema(Schema):
    flag = fields.Boolean(required=True, dump_default=False)

    @post_load
    def make_init_db(self, data: dict, **kwargs: dict) -> InitDB:
        return InitDB(**data)
