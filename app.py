from fastapi import FastAPI, Header, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from stream_service import stream_file
from firebase_service import initialize

app = FastAPI(
    title="Multipart Streaming Server",
    version="1.0.0"
)

# ---------- CORS ----------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
       "https://deep-bkl.web.app/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Startup ----------

@app.on_event("startup")
def startup():

    initialize()

    print("Firebase initialized")


# ---------- Health ----------

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# ---------- Stream ----------

@app.get("/stream/{file_id}")
def stream(
    file_id: str,
    range: str | None = Header(
        default=None,
        alias="Range"
    )
):

    return stream_file(
        file_id,
        range
    )


# ---------- Root ----------

@app.get("/")
def root():

    return JSONResponse(
        {
            "service": "Multipart Streaming Server",
            "version": "1.0.0",
            "health": "/health"
        }
    )
