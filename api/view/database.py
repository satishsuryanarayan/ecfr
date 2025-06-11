from flask.views import MethodView
from flask_smorest import abort, Blueprint

from api.controller.database import DatabaseController
from api.dtos.initdb import InitDB, InitDBSchema

database: Blueprint = Blueprint("Database", "Database", description="Database API")


@database.route("/initialize")
class DatabaseView(MethodView):
    @database.doc(description="Create tables and initialize the database.")
    @database.arguments(schema=InitDBSchema)
    @database.response(status_code=201)
    def post(self, init_db: InitDB) -> None:
        try:
            DatabaseController.initialize(init_db.force)
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))
