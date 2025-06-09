from typing import Sequence, List, Dict, Any

from flask import current_app
from marshmallow import Schema
from sqlalchemy import Connection, RowMapping
from sqlalchemy.engine.result import MappingResult
from sqlalchemy.sql.base import ColumnCollection

chunk_size = 1000


# Generator to stream result list
def list_generator(cursor: MappingResult, connection: Connection, schema: Schema,
                   size=chunk_size):
    try:
        yield "["
        results: Sequence[RowMapping] = cursor.fetchmany(size=size)
        while results:
            serialized_data: List[str] = []
            for row in results:
                instance = schema.load(row)
                serialized_data.append(schema.dumps(instance))
            yield ", ".join(serialized_data)
            results: Sequence[RowMapping] = cursor.fetchmany(size=size)
        yield "]"
    except Exception as e:
        current_app.logger.warning("Unknown error in data generator list: %s", e, exc_info=True)
    finally:
        connection.commit()
        cursor.close()


# Generator to stream result group list
def group_list_generator(cursor: MappingResult, connection: Connection, schema: Schema,
                         group: ColumnCollection, list_key: str,
                         list_keys: ColumnCollection, size=chunk_size):
    try:
        yield "["
        results: Sequence[RowMapping] = cursor.fetchmany(size=size)
        group_dict: Dict[str, Any] = dict()
        group_list: List[Dict[str, Any]] = list()
        if results:
            group_dict = {column.key: results[0][column] for column in group}
        while results:
            serialized_data = []
            for row in results:
                row_group = {column.key: results[0][column] for column in group}
                if row_group == group_dict:
                    group_list.append({column.key: row[column] for column in list_keys if column in row})
                else:
                    group_dict[list_key] = group_list
                    instance = schema.load(group_dict)
                    serialized_data.append(schema.dumps(instance))
                    group_dict = row_group
                    group_list = list()
                    group_list.append({column.key: row[column] for column in list_keys if column in row})
            yield ", ".join(serialized_data)
            results: Sequence[RowMapping] = cursor.fetchmany(size=size)
        yield "]"
    except Exception as e:
        current_app.logger.warning("Unknown error in data generator list: %s", e, exc_info=True)
    finally:
        connection.commit()
        cursor.close()
