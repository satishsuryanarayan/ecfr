from typing import cast

from flask import current_app, stream_with_context, Response
from sqlalchemy import select, ColumnElement, or_, MappingResult, exists
from sqlalchemy.engine import Connection, CursorResult
from sqlalchemy.exc import TimeoutError

from api.controller.utils.listgenerator import chunk_size, list_generator
from api.db import get_connection
from api.dtos.cfr_reference import CFRReferenceSchema, CFRReference
from api.model.agencies import Agencies
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
            with connection.begin():
                reference_exists: int = connection.execute(
                    select(exists().where(cast(ColumnElement[bool], CFR_References.c.id == cfr_reference_id)))).scalar()
                if not reference_exists:
                    raise AssertionError(f"CFR Reference with id={cfr_reference_id} does not exist")
                cursor: MappingResult = connection.execute(
                    select(CFR_References).where(
                        cast(ColumnElement[bool], CFR_References.c.id == cfr_reference_id))).mappings()
                schema: CFRReferenceSchema = CFRReferenceSchema()
                instance: CFRReference = schema.load(cursor.fetchone())
                cursor.close()
                return instance
        except Exception as e:
            current_app.logger.error("Exception while getting reference: %s", e, exc_info=True)
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
            current_app.logger.error("Exception while getting references: %s", e, exc_info=True)
            raise e

    @classmethod
    def get_references_by_agency(cls, agency_id: int) -> Response:
        current_app.logger.debug("Getting references by agency...")
        try:
            connection: Connection = get_connection(isolation_level="REPEATABLE READ")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            agency_exists: int = connection.execute(
                select(exists().where(cast(ColumnElement[bool], Agencies.c.id == agency_id)))).scalar()
            if not agency_exists:
                raise AssertionError(f"Agency with id={agency_id} does not exist")
            cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                select(CFR_References).where(
                    or_(CFR_References.c.agency_id == agency_id, CFR_References.c.parent_agency_id == agency_id)))
            return Response(stream_with_context(list_generator(cursor.mappings(), connection, CFRReferenceSchema())),
                            content_type="application/json")
        except Exception as e:
            connection.rollback()
            current_app.logger.error("Exception while getting references by agency: %s", e, exc_info=True)
            raise e
