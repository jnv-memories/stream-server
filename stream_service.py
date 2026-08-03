def stream_generator(
    parts,
    global_start,
    global_end
):
    """
    Streams only the requested byte ranges from the
    required multipart files.

    Browser  ---> This server ---> static.pw.live

    Memory usage stays very low because nothing is
    buffered except the current chunk.
    """

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