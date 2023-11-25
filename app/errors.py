"""Application specific custom exceptions"""


class TokenDecodingException(Exception):
    """Exception raised when an error occurs decoding a JWT token"""


class TokenExpiredException(Exception):
    """Exception raised when trying to decode an expired token"""
