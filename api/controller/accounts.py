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
from bank.dtos.account import Account, AccountSchema
from bank.dtos.balance import Balance, BalanceSchema
from bank.dtos.createaccount import CreateAccount
from bank.model.accounts import Accounts
from bank.model.balances import Balances
from bank.model.customers import Customers


class AccountsController:
    @classmethod
    def get_all_accounts(cls, from_time: datetime = None, to_time: datetime = None) -> Response:
        current_app.logger.debug("Getting all accounts...")
        try:
            connection: Connection = get_connection(isolation_level="REPEATABLE READ")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            if from_time is not None and to_time is not None:
                cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                    select(Accounts).where(
                        and_(Accounts.c.creation_time >= from_time, Accounts.c.creation_time <= to_time)).order_by(
                        Accounts.c.creation_time))
            elif from_time is not None and to_time is None:
                cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                    select(Accounts).where(Accounts.c.creation_time >= from_time).order_by(Accounts.c.creation_time))
            elif from_time is None and to_time is not None:
                cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                    select(Accounts).where(Accounts.c.creation_time <= to_time).order_by(Accounts.c.creation_time))
            else:
                cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                    select(Accounts).order_by(Accounts.c.creation_time))
        except Exception as e:
            connection.rollback()
            current_app.logger.error("Unknown error while getting all accounts: %s", e, exc_info=True)
            raise e

        return Response(stream_with_context(list_generator(cursor.mappings(), connection, AccountSchema())),
                        content_type="application/json")

    @classmethod
    def create_account(cls, crt_account: CreateAccount) -> Account:
        try:
            connection: Connection = get_connection(isolation_level="SERIALIZABLE")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            with connection.begin():
                customer_exists: int = connection.execute(select(
                    exists().where(cast(ColumnElement[bool], Customers.c.id == crt_account.customer_id)))).scalar()
                if not customer_exists:
                    raise AssertionError(f"Customer with id={crt_account.customer_id} does not exist")

                now: datetime = datetime.now()
                cursor: CursorResult = connection.execute(
                    insert(Accounts).values(customer_id=crt_account.customer_id, creation_time=now))
                account_id: int = cursor.inserted_primary_key[0]
                cursor.close()
                connection.execute(
                    insert(Balances).values(account_id=account_id, amount=crt_account.amount,
                                            last_updated_time=now)).close()
                account: Account = Account(account_id, crt_account.customer_id, now)
                return account
        except AssertionError as ae:
            current_app.logger.info("Forbidden: %s", ae, exc_info=True)
            raise ae
        except Exception as e:
            current_app.logger.error("Unknown error while creating account: %s", e, exc_info=True)
            raise e

    @classmethod
    def get_account(cls, account_id: int) -> Account:
        current_app.logger.debug("Getting account...")

        try:
            connection: Connection = get_connection(isolation_level="REPEATABLE READ")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            with connection.begin():
                account_exists: int = connection.execute(
                    select(exists().where(cast(ColumnElement[bool], Accounts.c.id == account_id)))).scalar()
                if not account_exists:
                    raise AssertionError(f"Account with id={account_id} does not exist")
                cursor: CursorResult = connection.execute(
                    select(Accounts).where(cast(ColumnElement[bool], Accounts.c.id == account_id)))
                schema: AccountSchema = AccountSchema()
                account: Account = schema.load(cursor.mappings().first())
                cursor.close()
                return account
        except AssertionError as ae:
            current_app.logger.info("Forbidden: %s", ae, exc_info=True)
            raise ae
        except Exception as e:
            current_app.logger.error("Unknown error while getting account: %s", e, exc_info=True)
            raise e

    @classmethod
    def get_customer_accounts(cls, customer_id: int) -> Response:
        current_app.logger.debug("Getting all accounts for customer...")

        try:
            connection: Connection = get_connection(isolation_level="REPEATABLE READ")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            customer_exists: int = connection.execute(
                select(exists().where(cast(ColumnElement[bool], Customers.c.id == customer_id)))).scalar()
            if not customer_exists:
                raise AssertionError(f"Customer with id={customer_id} does not exist")
            cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                select(Accounts).where(cast(ColumnElement[bool], Accounts.c.customer_id == customer_id)).order_by(
                    Accounts.c.id))
            return Response(
                stream_with_context(list_generator(cursor.mappings(), connection, AccountSchema())),
                content_type="application/json")
        except AssertionError as ae:
            connection.rollback()
            current_app.logger.info("Forbidden: %s", ae, exc_info=True)
            raise ae
        except Exception as e:
            connection.rollback()
            current_app.logger.error("Unknown error while getting customer accounts: %s", e, exc_info=True)
            raise e

    @classmethod
    def get_account_balance(cls, account_id: int) -> Balance:
        current_app.logger.debug("Getting account balance for a given account...")

        try:
            connection: Connection = get_connection(isolation_level="REPEATABLE READ")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            with connection.begin():
                account_exists: int = connection.execute(
                    select(exists().where(cast(ColumnElement[bool], Accounts.c.id == account_id)))).scalar()
                if not account_exists:
                    raise AssertionError(f"Account with id={account_id} does not exist")
                cursor: CursorResult = connection.execute(
                    select(Balances).where(cast(ColumnElement[bool], Balances.c.account_id == account_id)))
                schema: BalanceSchema = BalanceSchema()
                balance: Balance = schema.load(cursor.mappings().first())
                cursor.close()
                return balance
        except AssertionError as ae:
            current_app.logger.info("Forbidden: %s", ae, exc_info=True)
            raise ae
        except Exception as e:
            current_app.logger.error("Unknown error while getting account balance: %s", e, exc_info=True)
            raise e
