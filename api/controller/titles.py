from datetime import datetime
from typing import Dict, List, Any, cast, Sequence, Tuple, Set

import requests
from flask import current_app, stream_with_context, Response
from requests.adapters import HTTPAdapter
from sqlalchemy import insert, select, ColumnElement, MappingResult, exists, RowMapping, func
from sqlalchemy.engine import Connection, CursorResult
from sqlalchemy.exc import TimeoutError
from urllib3 import Retry

from api.controller.utils.listgenerator import chunk_size, group_list_generator, list_generator
from api.db import get_connection
from api.dtos.amendmentdate import AmendmentDateSchema
from api.dtos.issuedate import IssueDateSchema
from api.dtos.title import TitleSchema, Title
from api.model.amendments import Amendments
from api.model.titles import Titles

retry_strategy: Retry = Retry(
    total=5,
    respect_retry_after_header=True
)
adapter: HTTPAdapter = HTTPAdapter(max_retries=retry_strategy)


class TitlesController:
    @classmethod
    def get_title(cls, title_number: int) -> Title:
        current_app.logger.debug("Getting title...")
        try:
            connection: Connection = get_connection(isolation_level="REPEATABLE READ")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            title_exists: int = connection.execute(
                select(exists().where(cast(ColumnElement[bool], Titles.c.number == title_number)))).scalar()
            if not title_exists:
                raise AssertionError(f"Title with number={title_number} does not exist")
            cursor: MappingResult = connection.execute(
                select(Titles, Amendments).select_from(
                    Titles.join(Amendments, Titles.c.number == Amendments.c.title)).where(
                    cast(ColumnElement[bool], Titles.c.number == title_number)).order_by(
                    Amendments.c.issue_date)).mappings()
            mappings: Sequence[RowMapping] = cursor.fetchall()
            grouped_by_title: Dict[str, Any] = {column.key: mappings[0][column] for column in Titles.columns}
            grouped_by_title["amendments"] = [{column.key: row[column] for column in Amendments.columns
                                               if column in row} for row in mappings]
            schema: TitleSchema = TitleSchema()
            instance: Title = schema.load(grouped_by_title)
            cursor.close()
            return instance
        except Exception as e:
            connection.rollback()
            current_app.logger.error("Exception while getting title: %s", e, exc_info=True)
            raise e

    @classmethod
    def get_titles(cls) -> Response:
        current_app.logger.debug("Getting titles...")
        try:
            connection: Connection = get_connection(isolation_level="REPEATABLE READ")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            cursor: CursorResult = connection.execution_options(stream_results=True, yield_per=chunk_size).execute(
                select(Titles, Amendments).select_from(
                    Titles.join(Amendments, Titles.c.number == Amendments.c.title)).order_by(Titles.c.number,
                                                                                    Amendments.c.issue_date))
            return Response(stream_with_context(group_list_generator(cursor.mappings(), connection, TitleSchema(),
                                                                     Titles.columns, "amendments",
                                                                     Amendments.columns)),
                            content_type="application/json")
        except Exception as e:
            connection.rollback()
            current_app.logger.error("Exception while getting titles: %s", e, exc_info=True)
            raise e

    @classmethod
    def create_titles(cls) -> None:
        current_app.logger.debug("Creating titles...")
        try:
            connection: Connection = get_connection(isolation_level="SERIALIZABLE")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            with connection.begin():
                count: int = connection.execute(select(func.count(Titles.c.number))).scalar()
                if count > 0:
                    current_app.logger.debug("Titles already created.")
                    return

            with requests.session() as session:
                current_app.logger.debug("Getting titles from source...")
                session.mount("https://", adapter)
                session.headers.update({"Accept": "application/json"})
                titles_url: str = "https://www.ecfr.gov/api/versioner/v1/titles.json"
                response: requests.Response = session.get(titles_url)
                response.raise_for_status()
                data: Dict[str, List[Dict[str, Any]]] = response.json()
                titles_list: List[Dict[str, Any]] = data["titles"]
                current_app.logger.debug("Finished getting titles from source.")
                with connection.begin():
                    for title in titles_list:
                        title_number: int = title["number"]
                        connection.execute(insert(Titles).values(number=title_number, name=title["name"])).close()
                        amendments_url: str = f"https://www.ecfr.gov/api/versioner/v1/versions/title-{title_number}.json"
                        current_app.logger.debug(f"Getting amendments from source for title={title_number}...")
                        response: requests.Response = session.get(amendments_url)
                        response.raise_for_status()
                        data: Dict[str, List[Dict[str, Any]]] = response.json()
                        versions_list: List[Dict[str, Any]] = data["content_versions"]
                        unique_versions: Set[Tuple[str, str]] = set()
                        for version in versions_list:
                            unique_versions.add((version["amendment_date"], version["issue_date"]))
                        for version in unique_versions:
                            amendment_date: datetime = datetime.strptime(version[0], "%Y-%m-%d")
                            issue_date: datetime = datetime.strptime(version[1], "%Y-%m-%d")
                            connection.execute(
                                insert(Amendments).values(title=title_number, amendment_date=amendment_date,
                                                          issue_date=issue_date))
                        current_app.logger.debug(
                            f"Finished populating amendments for title={title_number}.")
        except Exception as e:
            current_app.logger.error("Exception while creating titles: %s", e, exc_info=True)
            raise e

    @classmethod
    def get_issue_dates(cls, title_number: int) -> Response:
        current_app.logger.debug("Getting issue dates...")
        try:
            connection: Connection = get_connection(isolation_level="REPEATABLE READ")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            title_exists: int = connection.execute(
                select(exists().where(cast(ColumnElement[bool], Titles.c.number == title_number)))).scalar()
            if not title_exists:
                raise AssertionError(f"Title with number={title_number} does not exist")
            cursor: CursorResult = connection.execute(
                select(Amendments.c.issue_date).distinct().where(
                    cast(ColumnElement[bool], Amendments.c.title == title_number)).order_by(
                    Amendments.c.issue_date))

            return Response(stream_with_context(list_generator(cursor.mappings(), connection, IssueDateSchema())),
                            content_type="application/json")
        except Exception as e:
            connection.rollback()
            current_app.logger.error("Exception while getting issue dates: %s", e, exc_info=True)
            raise e

    @classmethod
    def get_amendment_dates(cls, title_number: int) -> Response:
        current_app.logger.debug("Getting amendment dates...")
        try:
            connection: Connection = get_connection(isolation_level="REPEATABLE READ")
        except TimeoutError as pe:
            current_app.logger.warning("Not enough resources: %s", pe, exc_info=True)
            raise ResourceWarning(pe)

        try:
            title_exists: int = connection.execute(
                select(exists().where(cast(ColumnElement[bool], Titles.c.number == title_number)))).scalar()
            if not title_exists:
                raise AssertionError(f"Title with number={title_number} does not exist")
            cursor: CursorResult = connection.execute(
                select(Amendments.c.amendment_date).distinct().where(
                    cast(ColumnElement[bool], Amendments.c.title == title_number)).order_by(
                    Amendments.c.amendment_date))

            return Response(stream_with_context(list_generator(cursor.mappings(), connection, AmendmentDateSchema())),
                            content_type="application/json")
        except Exception as e:
            connection.rollback()
            current_app.logger.error("Exception while getting amendment dates: %s", e, exc_info=True)
            raise e
