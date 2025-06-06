from datetime import datetime
from typing import cast

from flask import current_app, stream_with_context, Response
from sqlalchemy import insert, select, and_
from sqlalchemy.engine import Connection, CursorResult
from sqlalchemy.exc import TimeoutError
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.expression import exists

from bank.controller.utils.listgenerator import chunk_size, list_generator
from bank.db import get_connection
from bank.dtos.createcustomer import CreateCustomer
from bank.dtos.customer import Customer, CustomerSchema
from bank.model.customers import Customers


class CustomersController:
    @classmethod
    def get_all_customers(cls, from_time: datetime = None, to_time: datetime = None) -> Response:
        current_app.logger.debug("Getting all customers...")
        try:
            connection: Connection = get_connection(isolation_level="REPEATABLE READ")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            if from_time is not None and to_time is not None:
                cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                    select(Customers).where(
                        and_(Customers.c.creation_time >= from_time, Customers.c.creation_time <= to_time)).order_by(
                        Customers.c.creation_time))
            elif from_time is not None and to_time is None:
                cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                    select(Customers).where(Customers.c.creation_time >= from_time).order_by(Customers.c.creation_time))
            elif from_time is None and to_time is not None:
                cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                    select(Customers).where(Customers.c.creation_time <= to_time).order_by(Customers.c.creation_time))
            else:
                cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                    select(Customers).order_by(Customers.c.creation_time))
        except Exception as e:
            connection.rollback()
            current_app.logger.error("Unknown error while creating customer: %s", e, exc_info=True)
            raise e

        return Response(stream_with_context(list_generator(cursor.mappings(), connection, CustomerSchema())),
                        content_type="application/json")

    @classmethod
    def create_customer(cls, crt_customer: CreateCustomer) -> Customer:
        try:
            connection: Connection = get_connection(isolation_level="SERIALIZABLE")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            with connection.begin():
                now: datetime = datetime.now()
                cursor: CursorResult = connection.execute(
                    insert(Customers).values(name=crt_customer.name, creation_time=now))
                customer_id: int = cursor.inserted_primary_key[0]
                cursor.close()
                customer: Customer = Customer(customer_id, crt_customer.name, now)
                return customer
        except Exception as e:
            current_app.logger.error("Unknown error while creating customer: %s", e, exc_info=True)
            raise e

    @classmethod
    def get_customer(cls, customer_id: int) -> Customer:
        current_app.logger.debug("Getting customer...")
        try:
            connection: Connection = get_connection(isolation_level="REPEATABLE READ")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            with connection.begin():
                customer_exists: int = connection.execute(
                    select(exists().where(cast(ColumnElement[bool], Customers.c.id == customer_id)))).scalar()
                if not customer_exists:
                    raise AssertionError(f"Customer with id={customer_id} does not exist")
                cursor: CursorResult = connection.execute(
                    select(Customers).where(cast(ColumnElement[bool], Customers.c.id == customer_id)))
                schema: CustomerSchema = CustomerSchema()
                customer: Customer = schema.load(cursor.mappings().first())
                cursor.close()
                return customer
        except Exception as e:
            current_app.logger.error("Unknown error while getting customer: %s", e, exc_info=True)
            raise e
