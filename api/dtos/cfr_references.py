from marshmallow import Schema, fields, post_load


class CFRReferences:
    def __init__(self, id: int, agency_id: int, parent_agency_id: int, reference: dict) -> None:
        self.id = id
        self.agency_id = agency_id
        self.parent_agency_id = parent_agency_id
        self.reference = reference

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, agency_id={self.agency_id}, parent_agency_id={self.parent_agency_id}, reference={self.reference})"


class CFRReferenceSchema(Schema):
    id = fields.Integer(required=True)
    agency_id = fields.Integer(required=True)
    parent_agency_id = fields.Integer(required=False, allow_none=True)
    reference = fields.Dict(required=True)

    @post_load
    def make_cfr_reference(self, data: dict, **kwargs: dict) -> CFRReferences:
        return CFRReferences(**data)
