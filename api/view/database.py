from flask.views import MethodView
from flask_smorest import abort, Blueprint

from api.controller.database import DatabaseController
from api.dtos.forceinit import ForceInit, ForceInitSchema

database: Blueprint = Blueprint("Database", "Database", description="Database API")


@database.route("/init-db")
class DatabaseView(MethodView):
    @database.doc(description="Create tables and initialize the database.")
    @database.arguments(schema=ForceInitSchema)
    @database.response(status_code=201)
    def post(self, force_init: ForceInit) -> None:
        try:
            DatabaseController.init_db(force_init.flag)
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))
