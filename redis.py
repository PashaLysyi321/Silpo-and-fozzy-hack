from aioredis import from_url

from settings import REDIS_URL

client = from_url(REDIS_URL)
