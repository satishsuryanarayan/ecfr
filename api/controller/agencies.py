from typing import Dict, List, Any, cast, Sequence

import requests
from flask import current_app, stream_with_context, Response
from requests.adapters import HTTPAdapter
from sqlalchemy import insert, select, ColumnElement, MappingResult, exists, RowMapping
from sqlalchemy.engine import Connection, CursorResult
from sqlalchemy.exc import TimeoutError
from urllib3 import Retry

from api.controller.utils.listgenerator import chunk_size, group_list_generator
from api.db import get_connection
from api.dtos.agency import AgencySchema, Agency
from api.model.agencies import Agencies
from api.model.cfr_references import CFR_References

retry_strategy: Retry = Retry(
    total=5,
    backoff_factor=1
)
adapter: HTTPAdapter = HTTPAdapter(max_retries=retry_strategy)


class AgenciesController:
    @classmethod
    def get_agency(cls, agency_id: int) -> Agency:
        current_app.logger.debug("Getting agency...")
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
            cursor: MappingResult = connection.execute(
                Agencies.join(CFR_References, Agencies.c.id == CFR_References.c.agency_id).select().where(
                    cast(ColumnElement[bool], Agencies.c.id == agency_id))).mappings()
            mappings: Sequence[RowMapping] = cursor.fetchall()
            grouped_by_agency: Dict[str, Any] = {key: mappings[0][key] for key in Agencies.columns}
            grouped_by_agency["cfr_references"] = [{k: d[k] for k in CFR_References.columns if k in d} for d in
                                                   mappings]
            current_app.logger.debug(grouped_by_agency)
            schema: AgencySchema = AgencySchema()
            instance: Agency = schema.load(grouped_by_agency)
            cursor.close()
            return instance
        except Exception as e:
            connection.rollback()
            current_app.logger.error("Exception while getting agency: %s", e, exc_info=True)
            raise e

    @classmethod
    def get_agencies(cls) -> Response:
        current_app.logger.debug("Getting agencies...")
        try:
            connection: Connection = get_connection(isolation_level="REPEATABLE READ")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                Agencies.join(CFR_References, Agencies.c.id == CFR_References.c.agency_id).select().order_by(
                    Agencies.columns))
            return Response(stream_with_context(group_list_generator(cursor.mappings(), connection, AgencySchema(),
                                    Agencies.columns, "cfr_references", CFR_References.columns)),
                            content_type="application/json")
        except Exception as e:
            connection.rollback()
            current_app.logger.error("Exception while getting agencies: %s", e, exc_info=True)
            raise e

    @classmethod
    def create_agencies(cls) -> None:
        current_app.logger.debug("Creating agencies...")
        try:
            connection: Connection = get_connection(isolation_level="SERIALIZABLE")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            with requests.session() as session:
                current_app.logger.debug("Getting agencies from source...")
                session.mount("https://", adapter)
                session.headers.update({"Accept": "application/json"})
                agencies_url: str = "https://www.ecfr.gov/api/admin/v1/agencies.json"
                response = session.get(agencies_url)
                data: Dict[str, List[Dict[str, Any]]] = response.json()
                agency_list: List[Dict[str, Any]] = data["agencies"]
                current_app.logger.debug("Finished getting agencies from source.")

            with connection.begin():
                for agency in agency_list:
                    cursor: CursorResult = connection.execute(
                        insert(Agencies).values(parent_id=None, short_name=agency["short_name"],
                                                name=agency["display_name"]))
                    agency_id: int = cursor.inserted_primary_key[0]
                    cursor.close()
                    for cfr_reference in agency["cfr_references"]:
                        connection.execute(insert(CFR_References).values(agency_id=agency_id, parent_agency_id=None,
                                                                         reference=cfr_reference)).close()

                    for child in agency["children"]:
                        cursor: CursorResult = connection.execute(
                            insert(Agencies).values(parent_id=agency_id, short_name=child["short_name"],
                                                    name=child["display_name"]))
                        child_agency_id: int = cursor.inserted_primary_key[0]
                        cursor.close()
                        for cfr_reference in child["cfr_references"]:
                            connection.execute(insert(CFR_References).values(agency_id=child_agency_id,
                                                                             parent_agency_id=agency_id,
                                                                             reference=cfr_reference)).close()
        except Exception as e:
            current_app.logger.error("Exception while creating agencies: %s", e, exc_info=True)
            raise e
