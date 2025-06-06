from flask import Response
from flask.views import MethodView
from flask_smorest import abort, Blueprint

from api.controller.agencies import AgenciesController
from api.dtos.agency import AgencySchema

agencies: Blueprint = Blueprint("Agencies", "Agencies", description="Agencies API")


@agencies.route("/agencies")
class AgenciesView(MethodView):
    @agencies.doc(description="Get agencies list")
    @agencies.response(status_code=200, schema=AgencySchema(many=True))
    def get(self) -> Response:
        try:
            return AgenciesController.get_agencies()
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))

    @agencies.doc(description="Create agencies and their CFR references")
    @agencies.response(status_code=201)
    def post(self) -> None:
        try:
            AgenciesController.create_agencies()
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))
