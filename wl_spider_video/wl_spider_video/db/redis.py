import redis

REDIS_HOST = "127.0.0.1"
REDIS_PORT = "6379"
REDIS_DB = 5

pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
redis_cli = redis.Redis(connection_pool=pool, decode_responses=True)
