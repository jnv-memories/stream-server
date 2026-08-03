import requests

from config import (
    REQUEST_TIMEOUT,
    USER_AGENT
)

session = requests.Session()

session.headers.update({
    "User-Agent": USER_AGENT
})

adapter = requests.adapters.HTTPAdapter(

    pool_connections=50,

    pool_maxsize=50,

    max_retries=2

)

session.mount(
    "https://",
    adapter
)

session.mount(
    "http://",
    adapter
)

DEFAULT_TIMEOUT = REQUEST_TIMEOUT