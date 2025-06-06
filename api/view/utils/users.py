from flask.views import MethodView
from flask_smorest import abort, Blueprint

from bank.controller.utils.users import UsersController
from bank.dtos.utils.createuser import CreateUserSchema, CreateUser
from bank.dtos.utils.user import UserSchema, User

users: Blueprint = Blueprint("Users", "Users", description="Register User API")


@users.route("/users")
class RegisterUsersView(MethodView):
    @users.doc(description="Register a new user")
    @users.response(status_code=201, schema=UserSchema)
    @users.arguments(schema=CreateUserSchema)
    def post(self, create_user: CreateUser) -> User:
        try:
            return UsersController.register_user(create_user)
        except ResourceWarning as rw:
            abort(503, rw, message=repr(rw))
        except AssertionError as ae:
            abort(422, ae, message=repr(ae))
        except Exception as e:
            abort(500, e, message=repr(e))
