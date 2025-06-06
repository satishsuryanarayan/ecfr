import xml.etree.ElementTree as ElementTree
from datetime import datetime
from typing import cast

import requests
from flask import current_app, stream_with_context, Response
from requests.adapters import HTTPAdapter
from sqlalchemy import insert, select, and_, ColumnElement, exists, or_, MappingResult
from sqlalchemy.engine import Connection, CursorResult
from sqlalchemy.exc import TimeoutError
from urllib3 import Retry

from api.controller.utils.listgenerator import chunk_size, list_generator
from api.controller.utils.wordcount import count_words
from api.db import get_connection
from api.dtos.agency import AgencySchema
from api.model.agencies import Agencies
from api.model.cfr_insights import CFR_Insights
from api.model.cfr_references import CFR_References

retry_strategy: Retry = Retry(
    total=5,
    backoff_factor=1
)
adapter: HTTPAdapter = HTTPAdapter(max_retries=retry_strategy)


class CFRInsightsController:
    @classmethod
    def get_insights(cls, agency_id: str, from_date: datetime = None, to_date: datetime = None) -> Response:
        current_app.logger.debug("Getting insights...")
        try:
            connection: Connection = get_connection(isolation_level="REPEATABLE READ")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            if from_date is not None and to_date is not None:
                cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                    select(CFR_Insights).where(
                        and_(CFR_Insights.c.agency_id == agency_id, CFR_Insights.c.from_date >= from_date,
                             CFR_Insights.to_date <= to_date)))
            elif from_date is not None and to_date is None:
                cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                    select(CFR_Insights).where(
                        and_(CFR_Insights.c.agency_id == agency_id, CFR_Insights.c.from_date >= from_date)))
            elif from_date is None and to_date is not None:
                cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                    select(CFR_Insights).where(
                        and_(CFR_Insights.c.agency_id == agency_id, CFR_Insights.c.to_date <= to_date)))
            else:
                cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                    select(CFR_Insights).where(cast(ColumnElement[bool], CFR_Insights.c.agency_id == agency_id)))
            return Response(stream_with_context(list_generator(cursor.mappings(), connection, AgencySchema())),
                            content_type="application/json")
        except Exception as e:
            connection.rollback()
            current_app.logger.error("Unknown error while getting agencies: %s", e, exc_info=True)
            raise e

    @classmethod
    def create_insights(cls, agency_id: str, date: datetime) -> None:
        current_app.logger.debug("Creating insights...")
        try:
            connection: Connection = get_connection(isolation_level="SERIALIZABLE")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            agency_exists: int = connection.execute(
                select(exists().where(cast(ColumnElement[bool], Agencies.c.id == agency_id)))).scalar()
            if not agency_exists:
                raise AssertionError(f"Agency with id={agency_id} does not exist")
            parent_id: str = connection.execute(
                select(Agencies.c.parent_id).where(cast(ColumnElement[bool], Agencies.c.id == agency_id))).scalar()
            if parent_id:
                agency_id = parent_id
            current_app.logger.debug("Creating insight for id=%s", agency_id)

            cursor: MappingResult = connection.execute(select(CFR_References.c.id, CFR_References.c.reference).where(
                or_(CFR_References.c.agency_id == agency_id,
                    CFR_References.c.parent_agency_id == agency_id))).mappings()
            results = cursor.fetchall()
            cursor.close()
            for result in results:
                cfr_reference_id: int = result["id"]
                reference: dict = result["reference"]
                title = reference["title"]
                del reference["title"]
                with requests.session() as session:
                    current_app.logger.debug("Getting xml from source...")
                    session.mount("https://", adapter)
                    session.headers.update({"Accept": "application/xml"})
                    formatted_date = date.strftime("%Y-%m-%d")
                    xml_url: str = f"https://www.ecfr.gov/api/versioner/v1/full/{formatted_date}/title-{title}.xml?"
                    xml_url += "&".join(f"{key}={value}" for key, value in reference.items())
                    response = session.get(xml_url)
                    root: ElementTree.Element = ElementTree.fromstring(response.content)
                    total_word_count: int = 0
                    total_restrictive_terms_word_count: int = 0
                    for elem in root.iter():
                        if elem.text:
                            word_count, restrictive_terms_word_count = count_words(elem.text.strip())
                            total_word_count += word_count
                            total_restrictive_terms_word_count += restrictive_terms_word_count
                    current_app.logger.debug("Finished getting agencies from source.")

                with connection.begin():
                    connection.execute(insert(CFR_Insights).values(cfr_reference_id=cfr_reference_id, date=date,
                                                                   word_count=total_word_count,
                                                                   restrictive_terms_word_count=total_restrictive_terms_word_count)).close()
        except Exception as e:
            current_app.logger.error("Unknown error while creating customer: %s", e, exc_info=True)
            raise e
