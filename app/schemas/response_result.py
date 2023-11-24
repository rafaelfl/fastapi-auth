"""Data format for the API responses"""
from typing import Union, Any
from pydantic import BaseModel


class ResponseResult(BaseModel):
    """Default response format"""

    status: bool
    message: str
    data: Union[Any, None] = None
