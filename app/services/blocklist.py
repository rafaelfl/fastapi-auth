"""Block list service based on Redis

To improve the decoupling it would be
interesting to create a common interface
to handle with Redis without using directly
Redis package, but for this test project
it's fine.
"""
from datetime import datetime
from redis import Redis

class BlockListService:
    """Block list service class"""

    def __init__(self, redis: Redis):
        self.redis = redis

    def add_token_to_blocklist(self, token: str, exp: datetime):
        """Function used to add a new token in the block list during and an expiration time"""
        token_key = f"bl_{token}"
        self.redis.set(token_key, token)
        self.redis.expireat(token_key, exp)

    def is_token_blocked(self, token: str):
        """Function to check if there's a token value in the block list"""
        token_key = f"bl_{token}"
        val = self.redis.get(token_key)

        return bool(val)
