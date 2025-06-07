from typing import cast

from flask import current_app, stream_with_context, Response
from sqlalchemy import select, ColumnElement
from sqlalchemy.engine import Connection, CursorResult
from sqlalchemy.exc import TimeoutError

from api.controller.utils.listgenerator import chunk_size, list_generator
from api.db import get_connection
from api.dtos.cfr_reference import CFRReferenceSchema, CFRReference
from api.model.cfr_references import CFR_References


class CFRReferencesController:
    @classmethod
    def get_reference(cls, cfr_reference_id: int) -> CFRReference:
        current_app.logger.debug("Getting reference...")
        try:
            connection: Connection = get_connection(isolation_level="REPEATABLE READ")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            cursor: CursorResult = connection.execute(
                select(CFR_References).where(cast(ColumnElement[bool], CFR_References.c.id == cfr_reference_id)))
            schema: CFRReferenceSchema = CFRReferenceSchema()
            instance: CFRReference = schema.load(cursor.fetchone())
            cursor.close()
            return instance
        except Exception as e:
            connection.rollback()
            current_app.logger.error("Unknown error while getting reference: %s", e, exc_info=True)
            raise e

    @classmethod
    def get_references(cls) -> Response:
        current_app.logger.debug("Getting references...")
        try:
            connection: Connection = get_connection(isolation_level="REPEATABLE READ")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                select(CFR_References))
            return Response(stream_with_context(list_generator(cursor.mappings(), connection, CFRReferenceSchema())),
                            content_type="application/json")
        except Exception as e:
            connection.rollback()
            current_app.logger.error("Unknown error while getting references: %s", e, exc_info=True)
            raise e
