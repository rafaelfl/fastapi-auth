"""Main module for the REST API"""
import uvicorn
from fastapi import FastAPI
from app.schemas.response_result import ResponseResult

from app.routers import auth

app = FastAPI()

app.include_router(auth.router, tags=["auth"])


@app.get("/", response_model=ResponseResult, response_model_exclude_unset=True)
async def root() -> ResponseResult:
    """Root test endpoint"""
    return {"status": True, "message": "Hello FastAPI!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
