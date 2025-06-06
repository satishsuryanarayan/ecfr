from datetime import datetime
from decimal import Decimal
from typing import cast

from flask import current_app, stream_with_context, Response
from sqlalchemy import insert, select, update, and_, or_
from sqlalchemy.engine import Connection, CursorResult
from sqlalchemy.exc import TimeoutError
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.expression import exists

from bank.controller.utils.listgenerator import chunk_size, list_generator
from bank.db import get_connection
from bank.dtos.createtransfer import CreateTransfer
from bank.dtos.transfer import Transfer, TransferSchema
from bank.model.accounts import Accounts
from bank.model.balances import Balances
from bank.model.transfers import Transfers


class TransfersController:
    @classmethod
    def transfer_money(cls, create_transfer: CreateTransfer) -> Transfer:
        current_app.logger.debug("Transferring money between two existing accounts...")

        try:
            connection: Connection = get_connection(isolation_level="SERIALIZABLE")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            with connection.begin():
                from_exists: int = connection.execute(select(exists().where(
                    cast(ColumnElement[bool], Accounts.c.id == create_transfer.from_account_id)))).scalar()
                if not from_exists:
                    raise AssertionError(f"Account with id={create_transfer.from_account_id} does not exist")

                to_exists: int = connection.execute(select(
                    exists().where(cast(ColumnElement[bool], Accounts.c.id == create_transfer.to_account_id)))).scalar()
                if not to_exists:
                    raise AssertionError(f"Account with id={create_transfer.to_account_id} does not exist")

                """
                Consistent ordering of operations reduces the likelihood of deadlocks
                and, to that effect, whether transferring money from account 1 to account 2 or
                from account 2 to account 1, the database locks are acquired in the same order
                i.e. first lock for account 1 is acquired and then lock for account 2 is acquired.
                """
                if create_transfer.from_account_id < create_transfer.to_account_id:
                    from_account_balance: Decimal = connection.execute(select(Balances.c.amount).where(
                        cast(ColumnElement[bool],
                             Balances.c.account_id == create_transfer.from_account_id)).with_for_update()).scalar()
                    if from_account_balance < create_transfer.amount:
                        raise AssertionError(
                            f"Balance in account with id={create_transfer.from_account_id} is {from_account_balance} which is not enough to transfer {create_transfer.amount}")

                    to_account_balance: Decimal = connection.execute(select(Balances.c.amount).where(
                        cast(ColumnElement[bool],
                             Balances.c.account_id == create_transfer.to_account_id)).with_for_update()).scalar()
                else:
                    to_account_balance: Decimal = connection.execute(select(Balances.c.amount).where(
                        cast(ColumnElement[bool],
                             Balances.c.account_id == create_transfer.to_account_id)).with_for_update()).scalar()

                    from_account_balance: Decimal = connection.execute(select(Balances.c.amount).where(
                        cast(ColumnElement[bool],
                             Balances.c.account_id == create_transfer.from_account_id)).with_for_update()).scalar()
                    if from_account_balance < create_transfer.amount:
                        raise AssertionError(
                            f"Balance in account with id={create_transfer.from_account_id} is {from_account_balance} which is not enough to transfer {create_transfer.amount}")

                from_account_balance = from_account_balance - create_transfer.amount
                to_account_balance = to_account_balance + create_transfer.amount
                now: datetime = datetime.now()

                connection.execute(update(Balances).where(
                    cast(ColumnElement[bool], Balances.c.account_id == create_transfer.from_account_id)).values(
                    amount=from_account_balance, last_updated_time=now)).close()
                connection.execute(update(Balances).where(
                    cast(ColumnElement[bool], Balances.c.account_id == create_transfer.to_account_id)).values(
                    amount=to_account_balance, last_updated_time=now)).close()

                cursor: CursorResult = connection.execute(
                    insert(Transfers).values(from_account_id=create_transfer.from_account_id,
                                             to_account_id=create_transfer.to_account_id, amount=create_transfer.amount,
                                             time=now))
                transfer_id: int = cursor.inserted_primary_key[0]
                cursor.close()
                transfer: Transfer = Transfer(transfer_id, create_transfer.from_account_id,
                                              create_transfer.to_account_id, create_transfer.amount, now)
                return transfer
        except AssertionError as ae:
            current_app.logger.info("Forbidden: %s", ae, exc_info=True)
            raise ae
        except Exception as e:
            current_app.logger.error("Unknown error while transferring money: %s", e, exc_info=True)
            raise e

    @classmethod
    def get_account_transfers(cls, account_id: int, from_time: datetime = None, to_time: datetime = None) -> Response:
        current_app.logger.debug("Getting transfers for a given account...")

        try:
            connection: Connection = get_connection(isolation_level="REPEATABLE READ")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            account_exists: int = connection.execute(
                select(exists().where(cast(ColumnElement[bool], Accounts.c.id == account_id)))).scalar()
            if not account_exists:
                raise AssertionError(f"Account with id={account_id} does not exist")
            if from_time is not None and to_time is not None:
                cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                    select(Transfers).where(and_(and_(Transfers.c.time >= from_time, Transfers.c.time <= to_time),
                                                 or_(Transfers.c.from_account_id == account_id,
                                                     Transfers.c.to_account_id == account_id))).order_by(
                        Transfers.c.time))
            elif from_time is not None and to_time is None:
                cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                    select(Transfers).where(and_(Transfers.c.time >= from_time,
                                                 or_(Transfers.c.from_account_id == account_id,
                                                     Transfers.c.to_account_id == account_id))).order_by(
                        Transfers.c.time))
            elif from_time is None and to_time is not None:
                cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                    select(Transfers).where(and_(Transfers.c.time <= to_time,
                                                 or_(Transfers.c.from_account_id == account_id,
                                                     Transfers.c.to_account_id == account_id))).order_by(
                        Transfers.c.time))
            else:
                cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                    select(Transfers).where(
                        or_(Transfers.c.from_account_id == account_id,
                            Transfers.c.to_account_id == account_id)).order_by(Transfers.c.time))
            return Response(
                stream_with_context(list_generator(cursor.mappings(), connection, TransferSchema())),
                content_type="application/json")
        except AssertionError as ae:
            connection.rollback()
            current_app.logger.info("Forbidden: %s", ae, exc_info=True)
            raise ae
        except Exception as e:
            connection.rollback()
            current_app.logger.error("Unknown error while getting transfers for a given account: %s", e, exc_info=True)
            raise e

    @classmethod
    def get_transfer(cls, transfer_id: int) -> Transfer:
        current_app.logger.debug("Getting transfer...")

        try:
            connection: Connection = get_connection(isolation_level="REPEATABLE READ")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            with connection.begin():
                transfer_exists: int = connection.execute(
                    select(exists().where(cast(ColumnElement[bool], Transfers.c.id == transfer_id)))).scalar()
                if not transfer_exists:
                    raise AssertionError(f"Transfer with id={transfer_id} does not exist")
                cursor: CursorResult = connection.execute(
                    select(Transfers).where(cast(ColumnElement[bool], Transfers.c.id == transfer_id)))
                schema: TransferSchema = TransferSchema()
                transfer: Transfer = schema.load(cursor.mappings().first())
                cursor.close()
                return transfer
        except AssertionError as ae:
            current_app.logger.info("Forbidden: %s", ae, exc_info=True)
            raise ae
        except Exception as e:
            current_app.logger.error("Unknown error while getting transfers for a given account: %s", e, exc_info=True)
            raise e
