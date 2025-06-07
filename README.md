# ECFR Insights API 

## This API provides the following capabilities:

1. Actionable insights to be made on potential deregulation efforts across the government by providing KPIs such as:
   1. Word count growth is CFR over time
   2. Growth is restrictive terms ("shall", "must", "may not", "prohibited")
   3. Growth in the number of references over time
   4. Addition of subparts over time etc.
2. APIs to extract KPIs


## Instructions to run the server and use the API
1. Download and install Community Edition of MySQL from [here](https://www.mysql.com/products/community/)
2. Do the following steps on the mysql command line as mysql root user:
   1. `create user 'ecfr_user'@'localhost' identified by 'secret';`
   2. `create database ecfr;`
   3. `create database test_ecfr;`
   4. `grant all on `ecfr`.* to 'ecfr_user'@'localhost';`
   5. `grant all on `test_ecfr`.* to 'ecfr_user'@'localhost';`
3. Have environment variable ECFR_DB_CONFIG_FILE point to the database configuration file. Below is the contents of an example db_config.json file pointed to by the ECFR_DB_CONFIG_FILE environment variable:
```json
{
    "user": "ecfr_user",
    "host": "localhost",
    "database": "ecfr",
    "password": "secret"
}
```
4. `git clone https://github.com/satishsuryanarayan/ecfr`
5. `cd ecfr`
6. `python -m venv .venv`
7. `source .venv/bin/activate`
8. `pip install -U pip`
9. `pip install -e ".[dev]"`
10. `pytest`
11. Before starting the server for the first time, please run the following command to initialize the database:
    `flask -app api init-db`
12. After the database is initialized, please run the following command to run the server and the application:
   `gunicorn -w 4 --threads 2 "api:create_app()" --keep-alive 3600`
13. Please point your browser to http://127.0.0.1:8000/docs
14. You can also start jupyter lab in another shell, open ecfr_insights_demo.ipynb (included) and plot more data.