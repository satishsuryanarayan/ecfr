from flask import Response
from flask.views import MethodView
from flask_smorest import abort, Blueprint

from api.controller.cfr_insights import CFRInsightsController
from api.dtos.cfr_insight import CFRInsightSchema
from api.dtos.createinsight import CreateInsightSchema, CreateInsight
from api.dtos.fromtoquery import FromToQuerySchema, FromToQuery

insights: Blueprint = Blueprint("CFR Insights", "CFR Insights", description="CFR Insights API")


@insights.route("/insights/<int:agency_id>")
class CFRInsightsListView(MethodView):
    @insights.doc(description="Get insights list")
    @insights.arguments(schema=FromToQuerySchema, location="query")
    @insights.response(status_code=200, schema=CFRInsightSchema(many=True))
    def get(self, from_to_query: FromToQuery, agency_id: int) -> Response:
        try:
            return CFRInsightsController.get_insights(agency_id, from_to_query.from_date, from_to_query.to_date)
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))

    @insights.route("/insights")
    class CFRInsightsCreateView(MethodView):
        @insights.doc(description="Create CFR insights")
        @insights.response(status_code=201)
        @insights.arguments(schema=CreateInsightSchema)
        def post(self, create_insight: CreateInsight) -> None:
            try:
                CFRInsightsController.create_insights(create_insight.agency_id, create_insight.date)
            except ResourceWarning as rw:
                abort(503, rw, message=repr(rw))
            except AssertionError as ae:
                abort(422, ae, message=repr(ae))
            except Exception as e:
                abort(500, e, message=repr(e))
