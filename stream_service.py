from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import requests

from client import (
    session,
    DEFAULT_TIMEOUT
)

from config import (
    CHUNK_SIZE
)

from firebase_service import (
    get_metadata,
    get_parts_between
)


def stream_file(file_id: str, range_header: str | None):

    metadata = get_metadata(file_id)

    if metadata is None:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    if not metadata.get("multipart"):
        raise HTTPException(
            status_code=400,
            detail="Not a multipart file"
        )

    total_size = metadata["size"]

    start, end = parse_range(
        range_header,
        total_size
    )

    parts = get_parts_between(
        metadata["parts"],
        start,
        end
    )

    headers = {
        "Content-Type": metadata.get(
            "type",
            "application/octet-stream"
        ),
        "Accept-Ranges": "bytes",
        "Content-Range": f"bytes {start}-{end}/{total_size}",
        "Content-Length": str(end - start + 1)
    }

    return StreamingResponse(
        stream_generator(
            parts,
            start,
            end
        ),
        status_code=206,
        headers=headers
    )


def stream_generator(
    parts,
    global_start,
    global_end
):

    current_start = global_start

    for part in parts:

        part_start = part["start"]
        part_end = part["end"]

        local_start = max(
            0,
            current_start - part_start
        )

        local_end = min(
            part["size"] - 1,
            global_end - part_start
        )

        headers = {
            "Range": f"bytes={local_start}-{local_end}"
        }

        try:

            with session.get(
                part["url"],
                headers=headers,
                stream=True,
                timeout=DEFAULT_TIMEOUT
            ) as response:

                response.raise_for_status()

                for chunk in response.iter_content(
                    chunk_size=CHUNK_SIZE
                ):

                    if chunk:
                        yield chunk

        except requests.RequestException as e:

            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch part {part['index']}: {e}"
            )

        current_start = part_end + 1

        if current_start > global_end:
            break


def parse_range(
    range_header,
    total_size
):

    if not range_header:
        return 0, total_size - 1

    if not range_header.startswith("bytes="):
        raise HTTPException(
            416,
            "Invalid Range"
        )

    value = range_header[6:]

    start_str, end_str = value.split("-")

    if start_str == "":
        raise HTTPException(
            416,
            "Suffix ranges unsupported"
        )

    start = int(start_str)

    if end_str == "":
        end = total_size - 1
    else:
        end = int(end_str)

    start = max(start, 0)
    end = min(end, total_size - 1)

    if start > end:
        raise HTTPException(
            416,
            "Invalid Range"
        )

    return start, end