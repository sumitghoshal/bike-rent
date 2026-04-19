"""Helpers for serializing MongoDB documents to JSON-safe dicts."""
from bson import ObjectId
from datetime import datetime


def serial(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict."""
    if doc is None:
        return None
    out = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            out[k] = str(v)
        elif isinstance(v, datetime):
            out[k] = v.isoformat()
        elif isinstance(v, dict):
            out[k] = serial(v)
        elif isinstance(v, list):
            out[k] = [serial(i) if isinstance(i, dict) else
                      (str(i) if isinstance(i, ObjectId) else
                       (i.isoformat() if isinstance(i, datetime) else i))
                      for i in v]
        else:
            out[k] = v
    return out


def serial_list(docs: list) -> list:
    """Serialize a list of MongoDB documents."""
    return [serial(d) for d in docs]


def oid(id_str: str) -> ObjectId:
    """Convert string to ObjectId, raises ValueError if invalid."""
    try:
        return ObjectId(str(id_str))
    except Exception:
        raise ValueError(f"Invalid ID: {id_str}")
