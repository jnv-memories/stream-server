from firebase_admin import credentials
from firebase_admin import firestore
import firebase_admin
import json
import os

from cache import get, put
from config import (
    CACHE_TIME,
    FIREBASE_COLLECTION
)

_db = None


def initialize():

    global _db

    if _db is not None:
        return

    if firebase_admin._apps:
        _db = firestore.client()
        return

    if os.path.exists("firebase_key.json"):

        cred = credentials.Certificate(
            "firebase_key.json"
        )

    else:

        data = json.loads(
            os.environ[
                "FIREBASE_SERVICE_ACCOUNT"
            ]
        )

        cred = credentials.Certificate(
            data
        )

    firebase_admin.initialize_app(
        cred
    )

    _db = firestore.client()


def get_metadata(file_id):

    cached = get(file_id)

    if cached is not None:
        return cached

    initialize()

    doc = (
        _db
        .collection(FIREBASE_COLLECTION)
        .document(file_id)
        .get()
    )

    if not doc.exists:
        return None

    data = doc.to_dict()

    prepare_metadata(data)

    put(
        file_id,
        data,
        CACHE_TIME
    )

    return data


def prepare_metadata(data):

    if not data.get("multipart"):
        return

    parts = sorted(
        data["parts"],
        key=lambda p: p["index"]
    )

    current = 0

    for part in parts:

        if "start" not in part:

            part["start"] = current

        if "end" not in part:

            part["end"] = (
                current +
                part["size"] -
                1
            )

        current = (
            part["end"] + 1
        )

    data["parts"] = parts


def get_part(parts, byte):

    """
    Binary search would be overkill
    because most uploads have only
    a handful of parts.

    """

    for part in parts:

        if (
            part["start"] <=
            byte <=
            part["end"]
        ):
            return part

    return None


def get_parts_between(
    parts,
    start,
    end
):

    result = []

    for part in parts:

        if part["end"] < start:
            continue

        if part["start"] > end:
            break

        result.append(part)

    return result