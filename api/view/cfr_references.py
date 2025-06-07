from flask import Response
from flask.views import MethodView
from flask_smorest import abort, Blueprint

from api.controller.cfr_references import CFRReferencesController
from api.dtos.cfr_reference import CFRReferenceSchema, CFRReference

references: Blueprint = Blueprint("CFR References", "CFR References", description="CFR References API")


@references.route("/references")
class CFRReferencesView(MethodView):
    @references.doc(description="Get CFR references list")
    @references.response(status_code=200, schema=CFRReferenceSchema(many=True))
    def get(self) -> Response:
        try:
            return CFRReferencesController.get_references()
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))


@references.route("/references/<int:cfr_reference_id>")
class CFRReferenceView(MethodView):
    @references.doc(description="Get CFR reference by ID")
    @references.response(status_code=200, schema=CFRReferenceSchema(many=True))
    def get(self, cfr_reference_id: int) -> CFRReference:
        try:
            return CFRReferencesController.get_reference(cfr_reference_id)
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))
