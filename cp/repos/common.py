"""Shared helpers for repository models."""

from pydantic import BaseModel


def convert_model_to_sql(table: str, model: BaseModel):
    data = model.model_dump()
    cols = data.keys()
    vals = [data[c] for c in cols]
    placeholders = ", ".join(["%s"] * len(cols))
    stmt = f'INSERT INTO {table} ({", ".join(cols)}) VALUES ({placeholders})'
    return stmt, vals
