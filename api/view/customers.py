from flask import Response
from flask.views import MethodView
from flask_httpauth import HTTPBasicAuth
from flask_smorest import abort, Blueprint

from api.controller.customers import CustomersController
from api.controller.utils.users import UsersController
from api.dtos.createcustomer import CreateCustomer, CreateCustomerSchema
from api.dtos.customer import CustomerSchema, Customer
from api.dtos.fromtoquery import FromToQuerySchema, FromToQuery

customers: Blueprint = Blueprint("Customers", "Customers", description="Bank Customers API")
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password) -> bool:
    return UsersController.validate_user(username, password)


@customers.route("/customers")
class CustomersCreateAndListView(MethodView):
    @auth.login_required
    @customers.doc(description="Get all customers")
    @customers.arguments(schema=FromToQuerySchema, location="query")
    @customers.response(status_code=200, schema=CustomerSchema(many=True))
    def get(self, query_params: FromToQuery) -> Response:
        try:
            if query_params:
                return CustomersController.get_all_customers(query_params.from_time, query_params.to_time)
            else:
                return CustomersController.get_all_customers()
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))

    @auth.login_required
    @customers.doc(description="Create a new customer")
    @customers.response(status_code=201, schema=CustomerSchema)
    @customers.arguments(schema=CreateCustomerSchema)
    def post(self, create_customer: CreateCustomer) -> Customer:
        try:
            return CustomersController.create_customer(create_customer)
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))


@customers.route("/customers/<int:customer_id>")
class CustomersView(MethodView):
    @auth.login_required
    @customers.doc(description="Get customer details by customer ID")
    @customers.response(status_code=200, schema=CustomerSchema)
    def get(self, customer_id: int) -> Customer:
        try:
            return CustomersController.get_customer(customer_id)
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))
