from flask import Response
from flask.views import MethodView
from flask_httpauth import HTTPBasicAuth
from flask_smorest import abort, Blueprint

from api.controller.accounts import AccountsController
from api.controller.utils.users import UsersController
from api.dtos.account import AccountSchema, Account
from api.dtos.balance import BalanceSchema, Balance
from api.dtos.createaccount import CreateAccount, CreateAccountSchema
from api.dtos.fromtoquery import FromToQuerySchema, FromToQuery

accounts: Blueprint = Blueprint("Accounts", "Account", description="Bank Accounts API")
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password) -> bool:
    return UsersController.validate_user(username, password)


@accounts.route("/accounts")
class AccountsCreateAndListView(MethodView):
    @auth.login_required
    @accounts.doc(description="Get all accounts")
    @accounts.arguments(schema=FromToQuerySchema, location="query")
    @accounts.response(status_code=200, schema=AccountSchema(many=True))
    def get(self, query_params: FromToQuery) -> Response:
        try:
            if query_params:
                return AccountsController.get_all_accounts(query_params.from_time, query_params.to_time)
            else:
                return AccountsController.get_all_accounts()
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))

    @auth.login_required
    @accounts.doc(description="Create a new account with initial balance for an existing customer")
    @accounts.response(status_code=201, schema=AccountSchema)
    @accounts.arguments(schema=CreateAccountSchema)
    def post(self, create_account: CreateAccount) -> Account:
        try:
            return AccountsController.create_account(create_account)
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))


@accounts.route("/accounts/<int:account_id>")
class AccountsView(MethodView):
    @auth.login_required
    @accounts.doc(description="Get account details by account ID")
    @accounts.response(status_code=200, schema=AccountSchema)
    def get(self, account_id: int) -> Account:
        try:
            return AccountsController.get_account(account_id)
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))


@accounts.route("/accounts/balance/<int:account_id>")
class AccountsBalanceView(MethodView):
    @auth.login_required
    @accounts.doc(description="Get account balance by account ID")
    @accounts.response(status_code=200, schema=BalanceSchema)
    def get(self, account_id: int) -> Balance:
        try:
            return AccountsController.get_account_balance(account_id)
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))


@accounts.route("/accounts/customer/<int:customer_id>")
class AccountsForCustomerView(MethodView):
    @auth.login_required
    @accounts.doc(description="Get all accounts for customer by customer ID")
    @accounts.response(status_code=200, schema=AccountSchema(many=True))
    def get(self, customer_id: int) -> Response:
        try:
            return AccountsController.get_customer_accounts(customer_id)
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))
