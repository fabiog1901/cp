"""Message queue repository backed by CockroachDB/Postgres."""

from . import mq_queries


def insert_into_mq(
    msg_type: str,
    msg_data: dict,
    created_by: str,
):
    return mq_queries.insert_into_mq(msg_type, msg_data, created_by)
