from flask import Response
from flask.views import MethodView
from flask_smorest import abort, Blueprint

from api.controller.cfr_references import CFRReferencesController
from api.dtos.cfr_references import CFRReferenceSchema

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
