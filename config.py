import os

CACHE_TIME = 300

CHUNK_SIZE = 64 * 1024

FIREBASE_COLLECTION = "uploadedFiles"

REQUEST_TIMEOUT = (
    10,
    30
)

USER_AGENT = (
    "MultipartStream/1.0"
)

PORT = int(
    os.getenv(
        "PORT",
        "8000"
    )
)
