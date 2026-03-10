import redis
from typing import Optional, List


class RedisClient:
    def __init__(self, url: str, username: Optional[str] = None, password: Optional[str] = None):
        self.client = redis.from_url(url, username=username, password=password, decode_responses=True)

    def set(self, key: str, value: str, ex: Optional[int] = None):
        """Set a key with optional expiration time in seconds"""
        return self.client.set(key, value, ex=ex)

    def get(self, key: str):
        return self.client.get(key)

    def incrby(self, key: str, amount: int = 1):
        return self.client.incrby(key, amount)

    def decrby(self, key: str, amount: int = 1):
        return self.client.decrby(key, amount)

    def keys(self, pattern: str) -> List[str]:
        return self.client.keys(pattern)

    def mget(self, keys: List[str]):
        if not keys:
            return []
        return self.client.mget(keys)
    
    def delete(self, key: str):
        return self.client.delete(key)
    
    def exists(self, key: str) -> bool:
        """Check if a key exists"""
        return self.client.exists(key) > 0
    
    def ttl(self, key: str) -> int:
        """Get the time to live for a key in seconds"""
        return self.client.ttl(key)
    
    def close(self):
        try:
            self.client.close()
        except Exception:
            pass

