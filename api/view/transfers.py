from flask import Response
from flask.views import MethodView
from flask_httpauth import HTTPBasicAuth
from flask_smorest import abort, Blueprint

from api.controller.transfers import TransfersController
from api.controller.utils.users import UsersController
from api.dtos.createtransfer import CreateTransfer, CreateTransferSchema
from api.dtos.fromtoquery import FromToQuerySchema, FromToQuery
from api.dtos.transfer import TransferSchema, Transfer

transfers: Blueprint = Blueprint("Transfers", "Transfers", description="Bank Transfers API")
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password) -> bool:
    return UsersController.validate_user(username, password)


@transfers.route("/transfers/account/<int:account_id>", methods=["GET"])
class TransfersForAccountView(MethodView):
    @auth.login_required
    @transfers.doc(description="Get all transfers for account by account ID")
    @transfers.arguments(schema=FromToQuerySchema, location="query")
    @transfers.response(status_code=200, schema=TransferSchema(many=True))
    def get(self, query_params: FromToQuery, account_id: int) -> Response:
        try:
            if query_params:
                return TransfersController.get_account_transfers(account_id, query_params.from_time,
                                                                 query_params.to_time)
            else:
                return TransfersController.get_account_transfers(account_id)
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))


@transfers.route("/transfers")
class TransfersCreateView(MethodView):
    @auth.login_required
    @transfers.doc(description="Transfer money between two existing accounts")
    @transfers.arguments(schema=CreateTransferSchema)
    @transfers.response(status_code=201, schema=TransferSchema)
    def post(self, create_transfer: CreateTransfer) -> Transfer:
        try:
            return TransfersController.transfer_money(create_transfer)
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))


@transfers.route("/transfers/<int:transfer_id>")
class TransfersView(MethodView):
    @auth.login_required
    @transfers.doc(description="Get transfer details by transfer ID")
    @transfers.response(status_code=200, schema=TransferSchema)
    def get(self, transfer_id: int) -> Transfer:
        try:
            return TransfersController.get_transfer(transfer_id)
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))
