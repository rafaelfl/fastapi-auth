"""Main module for the REST API"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.version import __version__
from app.schemas.response_result import ResponseResult
from app.routers import auth


app = FastAPI(version=__version__)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "https://fastapi-auth.rafaelf.dev",
    "https://login.rafaelf.dev",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["auth"])


@app.get("/", response_model=ResponseResult, response_model_exclude_unset=True)
async def root() -> ResponseResult:
    """Root test endpoint"""
    return {"status": True, "message": "Hello FastAPI!"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
