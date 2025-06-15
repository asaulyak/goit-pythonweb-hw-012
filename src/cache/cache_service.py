"""
Cache service module.
This module provides Redis cache configuration and client setup
for the application's caching needs.
"""

import redis
from src.config import settings


redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_DB,
)

# Default time-to-live for cached items in seconds
DEFAULT_CACHE_TTL = 60
