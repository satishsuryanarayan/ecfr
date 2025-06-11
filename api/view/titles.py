from flask import Response
from flask.views import MethodView
from flask_smorest import abort, Blueprint

from api.controller.titles import TitlesController
from api.dtos.date import DateSchema
from api.dtos.title import TitleSchema, Title

titles: Blueprint = Blueprint("Titles", "Titles", description="Titles API")


@titles.route("/titles")
class TitlesView(MethodView):
    @titles.doc(description="Get titles list")
    @titles.response(status_code=200, schema=TitleSchema(many=True))
    def get(self) -> Response:
        try:
            return TitlesController.get_titles()
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))

    @titles.doc(description="Create titles and their amendments from source")
    @titles.response(status_code=201)
    def post(self) -> None:
        try:
            TitlesController.create_titles()
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))


@titles.route("/titles/<int:title_number>")
class TitleView(MethodView):
    @titles.doc(description="Get title by ID")
    @titles.response(status_code=200, schema=TitleSchema)
    def get(self, title_number: int) -> Title:
        try:
            return TitlesController.get_title(title_number)
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))


@titles.route("/titles/amendments/issue_dates/<int:title_number>")
class TitleAmendmentsIssueDateView(MethodView):
    @titles.doc(description="Get unique issue dates by title ID")
    @titles.response(status_code=200, schema=DateSchema(many=True))
    def get(self, title_number: int) -> Response:
        try:
            return TitlesController.get_issue_dates(title_number)
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))


@titles.route("/titles/amendments/amendment_dates/<int:title_number>")
class TitleAmendmentsIssueDateView(MethodView):
    @titles.doc(description="Get unique issue dates by title ID")
    @titles.response(status_code=200, schema=DateSchema(many=True))
    def get(self, title_number: int) -> Response:
        try:
            return TitlesController.get_amendment_dates(title_number)
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))
