from flask import current_app
from marshmallow import Schema
from sqlalchemy import Connection
from sqlalchemy.engine.result import MappingResult

chunk_size = 1000


# Generator to stream result list
def list_generator(cursor: MappingResult, connection: Connection, schema: Schema,
                   size=chunk_size):
    try:
        yield "["
        results = cursor.fetchmany(size=size)
        while results:
            serialized_data = []
            for row in results:
                instance = schema.load(row)
                serialized_data.append(schema.dumps(instance))
            yield ", ".join(serialized_data)
            results = cursor.fetchmany(size=size)
        yield "]"
    except Exception as e:
        current_app.logger.warning("Unknown error in data generator list: %s", e, exc_info=True)
    finally:
        connection.commit()
        cursor.close()
