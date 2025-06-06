import atexit
import json
import os

from flask import Flask
from flask_smorest import Api
from sqlalchemy import create_engine
from sqlalchemy.pool.impl import QueuePool

from api import db
from api.view.agencies import agencies
from api.view.cfr_insights import insights


class APIConfig:
    API_TITLE: str = "CFR Insights API"
    API_VERSION: str = "v1"
    OPENAPI_VERSION: str = "3.0.3"
    OPENAPI_URL_PREFIX: str = "/"
    OPENAPI_SWAGGER_UI_PATH: str = "/docs"
    OPENAPI_SWAGGER_UI_URL: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"


# Create and configure the Flask app
def create_app(test_config: dict = None) -> Flask:
    app: Flask = Flask(__name__)
    app.config.from_object(APIConfig)

    if (test_config is not None) and (test_config.get("TESTING", False) == True):
        env = "TEST_ECFR_DB_CONFIG_FILE"
    else:
        env = "ECFR_DB_CONFIG_FILE"

    db_config_file = os.environ.get(env, "db_config.json")
    try:
        with open(db_config_file, "r") as file:
            db_config = json.load(file)
            db_config["autocommit"] = False
    except FileNotFoundError as fnf:
        app.logger.error("Error: %s", fnf, exc_info=True)
    except json.JSONDecodeError as jde:
        app.logger.error("Error: %s", jde, exc_info=True)

    db_config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://{0}:{1}@{2}/{3}".format(db_config["user"],
                                                                                           db_config["password"],
                                                                                           db_config["host"],
                                                                                           db_config["database"])

    if (test_config is not None) and (test_config.get("TESTING", False) == True):
        app.config.from_mapping(test_config)
        app.config["SERIALIZABLE"] = create_engine(db_config["SQLALCHEMY_DATABASE_URI"],
                                                   isolation_level="SERIALIZABLE", poolclass=QueuePool,
                                                   pool_use_lifo=False, pool_size=2, max_overflow=0,
                                                   pool_pre_ping=True, pool_reset_on_return="rollback", pool_timeout=30)
        app.config["REPEATABLE READ"] = app.config["SERIALIZABLE"].execution_options(isolation_level="REPEATABLE READ")
    else:
        app.config["SERIALIZABLE"] = create_engine(db_config["SQLALCHEMY_DATABASE_URI"],
                                                   isolation_level="SERIALIZABLE", poolclass=QueuePool,
                                                   pool_use_lifo=False, pool_size=32, max_overflow=0,
                                                   pool_pre_ping=True, pool_reset_on_return="rollback", pool_timeout=30)
        app.config["REPEATABLE READ"] = app.config["SERIALIZABLE"].execution_options(isolation_level="REPEATABLE READ")

    def cleanup():
        app.config["SERIALIZABLE"].dispose()
        app.config["REPEATABLE READ"].dispose()

    atexit.register(cleanup)

    db.init_app(app)

    api: Api = Api(app)
    api.register_blueprint(agencies)
    api.register_blueprint(insights)

    return app
