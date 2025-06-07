import xml.etree.ElementTree as ElementTree
from datetime import datetime
from typing import cast

import requests
from flask import current_app, stream_with_context, Response
from requests.adapters import HTTPAdapter
from sqlalchemy import insert, select, and_, ColumnElement, exists, or_, MappingResult, RowMapping
from sqlalchemy.engine import Connection, CursorResult
from sqlalchemy.exc import TimeoutError
from urllib3 import Retry

from api.controller.utils.listgenerator import chunk_size, list_generator
from api.controller.utils.metrics import count_words
from api.db import get_connection
from api.dtos.cfr_insight import CFRInsightSchema
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
    def get_insights(cls, agency_id: int, from_date: datetime = None, to_date: datetime = None) -> Response:
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
                        and_(or_(CFR_Insights.c.agency_id == agency_id, CFR_Insights.c.parent_agency_id == agency_id), CFR_Insights.c.date >= from_date,
                             CFR_Insights.date <= to_date)))
            elif from_date is not None and to_date is None:
                cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                    select(CFR_Insights).where(
                        and_(or_(CFR_Insights.c.agency_id == agency_id, CFR_Insights.c.parent_agency_id == agency_id), CFR_Insights.c.date >= from_date)))
            elif from_date is None and to_date is not None:
                cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                    select(CFR_Insights).where(
                        and_(or_(CFR_Insights.c.agency_id == agency_id, CFR_Insights.c.parent_agency_id == agency_id), CFR_Insights.c.date <= to_date)))
            else:
                cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                    select(CFR_Insights).where(or_(CFR_Insights.c.agency_id == agency_id, CFR_Insights.c.parent_agency_id == agency_id)))
            return Response(stream_with_context(list_generator(cursor.mappings(), connection, CFRInsightSchema())),
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
            with connection.begin():
                agency_exists: int = connection.execute(
                    select(exists().where(cast(ColumnElement[bool], Agencies.c.id == agency_id)))).scalar()
                if not agency_exists:
                    raise AssertionError(f"Agency with id={agency_id} does not exist")
                parent_id: int = connection.execute(
                    select(Agencies.c.parent_id).where(cast(ColumnElement[bool], Agencies.c.id == agency_id))).scalar()
                if parent_id:
                    agency_id = parent_id  # Insights are always created at the parent level
                current_app.logger.debug("Creating insight for id=%s", agency_id)

                cursor: MappingResult = connection.execution_options(stream_results=True, yield_per=5).execute(
                    select(CFR_References).where(
                        or_(CFR_References.c.agency_id == agency_id,
                            CFR_References.c.parent_agency_id == agency_id))).mappings()
                result: RowMapping = cursor.fetchone()
                while result:
                    cfr_reference_id: int = result["id"]
                    reference: dict = result["reference"]
                    agency_id: int = result["agency_id"]
                    parent_agency_id: int = result["parent_agency_id"]
                    title = reference["title"]
                    del reference["title"]
                    current_app.logger.debug("Creating insight for cfr_reference_id=%s with agency_id=%s and parent_agency_id=%s",
                                             cfr_reference_id, agency_id, parent_agency_id)
                    with requests.session() as session:
                        current_app.logger.debug("Getting xml from source...")
                        session.mount("https://", adapter)
                        session.headers.update({"Accept": "application/xml"})
                        formatted_date = date.strftime("%Y-%m-%d")
                        xml_url: str = f"https://www.ecfr.gov/api/versioner/v1/full/{formatted_date}/title-{title}.xml?"
                        xml_url += "&".join(f"{key}={value}" for key, value in reference.items())
                        current_app.logger.debug("Calling xml url: %s", xml_url)
                        response = session.get(xml_url)
                        current_app.logger.debug("Received response from xml url: %s", xml_url)
                        root: ElementTree.Element = ElementTree.fromstring(response.content)
                        total_word_count: int = 0
                        total_restrictive_terms_count: int = 0
                        current_app.logger.debug("Computing metrics...")
                        for elem in root.iter():
                            if elem.text:
                                word_count, restrictive_terms_count = count_words(elem.text.strip())
                                total_word_count += word_count
                                total_restrictive_terms_count += restrictive_terms_count
                        current_app.logger.debug("Finished processing xml url: %s", xml_url)

                        connection.execute(
                            insert(CFR_Insights).values(cfr_reference_id=cfr_reference_id, agency_id=agency_id,
                                                        parent_agency_id=parent_agency_id, date=date,
                                                        word_count=total_word_count,
                                                        restrictive_terms_count=total_restrictive_terms_count)).close()
                    result = cursor.fetchone()
        except Exception as e:
            current_app.logger.error("Unknown error while creating customer: %s", e, exc_info=True)
            raise e
        finally:
            cursor.close()
