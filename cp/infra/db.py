"""Low-level database infrastructure."""

import os
from typing import Any

from psycopg.abc import Dumper
from psycopg.pq import Format
from psycopg.rows import class_row
from psycopg.types.array import ListDumper
from psycopg.types.json import Jsonb, JsonbDumper
from psycopg_pool import ConnectionPool

DB_URL = os.getenv("DB_URL")

if not DB_URL:
    raise EnvironmentError("DB_URL env variable not found!")


pool = ConnectionPool(DB_URL, kwargs={"autocommit": True})


class Dict2JsonbDumper(JsonbDumper):
    def dump(self, obj):
        return super().dump(Jsonb(obj))


class SelectorDumper(Dumper):
    """Choose the correct dumper for list payloads."""

    format = Format.BINARY
    oid = None

    _dict_dumper = Dict2JsonbDumper(list)
    _list_dumper = ListDumper(list)

    def upgrade(self, obj, format: Format) -> Dumper:
        if obj and isinstance(obj[0], dict):
            return self._dict_dumper
        return self._list_dumper


def execute_stmt(
    stmt: str,
    bind_args: tuple = (),
) -> None:
    with pool.connection() as conn:
        _register_dumpers(conn)

        with conn.cursor() as cur:
            try:
                stmt = _normalize_stmt(stmt)

                print(f"SQL> {stmt}; {bind_args}")
                cur.execute(stmt, bind_args)
            except Exception as err:
                print(f"SQL ERROR: {err}")
                raise err


def fetch_all(
    stmt: str,
    bind_args: tuple,
    row_type,
) -> list[Any]:
    with pool.connection() as conn:
        _register_dumpers(conn)

        with conn.cursor(row_factory=class_row(row_type)) as cur:
            try:
                stmt = _normalize_stmt(stmt)

                print(f"SQL> {stmt}; {bind_args}")
                cur.execute(stmt, bind_args)
                return cur.fetchall()
            except Exception as err:
                print(f"SQL ERROR: {err}")
                raise err


def fetch_one(
    stmt: str,
    bind_args: tuple,
    row_type,
) -> Any | None:
    with pool.connection() as conn:
        _register_dumpers(conn)

        with conn.cursor(row_factory=class_row(row_type)) as cur:
            try:
                stmt = _normalize_stmt(stmt)

                print(f"SQL> {stmt}; {bind_args}")
                cur.execute(stmt, bind_args)
                return cur.fetchone()
            except Exception as err:
                print(f"SQL ERROR: {err}")
                raise err


def fetch_scalar(
    stmt: str,
    bind_args: tuple = (),
) -> Any | None:
    with pool.connection() as conn:
        _register_dumpers(conn)

        with conn.cursor() as cur:
            try:
                stmt = _normalize_stmt(stmt)

                print(f"SQL> {stmt}; {bind_args}")
                cur.execute(stmt, bind_args)
                row = cur.fetchone()
                if row is None:
                    return None
                return row[0]
            except Exception as err:
                print(f"SQL ERROR: {err}")
                raise err


def _register_dumpers(conn) -> None:
    conn.adapters.register_dumper(set, ListDumper)
    conn.adapters.register_dumper(dict, Dict2JsonbDumper)
    conn.adapters.register_dumper(list, SelectorDumper)


def _normalize_stmt(stmt: str) -> str:
    return " ".join([s.strip() for s in stmt.split("\n")])
