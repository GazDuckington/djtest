"""Redis manager"""
import redis

redis_control = redis.Redis(host="localhost", port=6379,decode_responses=True)
