import os
import time
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import hashlib

try:
    import redis
except ImportError:
    redis = None

try:
    import orjson
except ImportError:
    import json
    class orjson:
        @staticmethod
        def dumps(x, **kwargs):
            return json.dumps(x).encode()
        
        @staticmethod
        def loads(x):
            return json.loads(x.decode() if isinstance(x, bytes) else x)

try:
    import polars as pl
except ImportError:
    pl = None

class CacheManager:
    """High-performance cache manager using Redis for sub-second response times."""
    
    def __init__(self):
        self.redis_client = None
        self.hit_count = 0
        self.miss_count = 0
        self.default_ttl = 3600  # 1 hour
        self.job_cache_prefix = "jobs:"
        self.h1b_cache_prefix = "h1b:"
        self.stats_cache_prefix = "stats:"
        
    def initialize(self):
        """Initialize Redis connection with optimized settings."""
        try:
            self.redis_client = redis.Redis(
                host=os.environ.get('REDIS_HOST', 'localhost'),
                port=int(os.environ.get('REDIS_PORT', 6379)),
                db=0,
                decode_responses=False,  # Keep binary for faster serialization
                socket_connect_timeout=1,
                socket_timeout=1,
                connection_pool_class_kwargs={
                    'max_connections': 50,
                    'retry_on_timeout': True
                },
                health_check_interval=30
            )
            
            # Test connection
            self.redis_client.ping()
            print("Redis cache manager initialized successfully")
            
        except Exception as e:
            print(f"Redis connection failed: {e}")
            print("Falling back to in-memory cache")
            self.redis_client = None
            self._fallback_cache = {}
    
    def _serialize_data(self, data: Any) -> bytes:
        """Ultra-fast JSON serialization using orjson."""
        return orjson.dumps(data, option=orjson.OPT_SERIALIZE_NUMPY)
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Ultra-fast JSON deserialization using orjson."""
        return orjson.loads(data)
    
    def get_jobs(self, cache_key: str) -> Optional[List[Dict]]:
        """Get jobs from cache with performance tracking."""
        try:
            if self.redis_client:
                cached_data = self.redis_client.get(f"{self.job_cache_prefix}{cache_key}")
                if cached_data:
                    self.hit_count += 1
                    return self._deserialize_data(cached_data)
            else:
                # Fallback to in-memory cache
                if cache_key in self._fallback_cache:
                    self.hit_count += 1
                    return self._fallback_cache[cache_key]['data']
            
            self.miss_count += 1
            return None
            
        except Exception as e:
            print(f"Cache get error: {e}")
            self.miss_count += 1
            return None
    
    def set_jobs(self, cache_key: str, jobs: List[Dict], ttl: int = None) -> bool:
        """Set jobs in cache with TTL."""
        try:
            ttl = ttl or self.default_ttl
            serialized_data = self._serialize_data(jobs)
            
            if self.redis_client:
                return self.redis_client.setex(
                    f"{self.job_cache_prefix}{cache_key}",
                    ttl,
                    serialized_data
                )
            else:
                # Fallback to in-memory cache
                self._fallback_cache[cache_key] = {
                    'data': jobs,
                    'expires_at': time.time() + ttl
                }
                return True
                
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def get_h1b_prediction(self, company: str, role: str) -> Optional[float]:
        """Get H1B prediction from cache."""
        try:
            cache_key = f"{company.lower()}:{role.lower()}"
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()
            
            if self.redis_client:
                cached_prediction = self.redis_client.get(f"{self.h1b_cache_prefix}{cache_key}")
                if cached_prediction:
                    return float(cached_prediction.decode())
            else:
                # Fallback cache
                if cache_key in self._fallback_cache:
                    return self._fallback_cache[cache_key]['data']
            
            return None
            
        except Exception as e:
            print(f"H1B cache get error: {e}")
            return None
    
    def set_h1b_prediction(self, company: str, role: str, prediction: float, ttl: int = 86400) -> bool:
        """Set H1B prediction in cache (24-hour TTL by default)."""
        try:
            cache_key = f"{company.lower()}:{role.lower()}"
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()
            
            if self.redis_client:
                return self.redis_client.setex(
                    f"{self.h1b_cache_prefix}{cache_key}",
                    ttl,
                    str(prediction)
                )
            else:
                # Fallback cache
                self._fallback_cache[cache_key] = {
                    'data': prediction,
                    'expires_at': time.time() + ttl
                }
                return True
                
        except Exception as e:
            print(f"H1B cache set error: {e}")
            return False
    
    def batch_get_h1b_predictions(self, company_role_pairs: List[tuple]) -> Dict[str, Optional[float]]:
        """Batch get H1B predictions for better performance."""
        results = {}
        
        try:
            if self.redis_client:
                # Build cache keys
                cache_keys = []
                original_keys = []
                
                for company, role in company_role_pairs:
                    original_key = f"{company}:{role}"
                    cache_key = f"{company.lower()}:{role.lower()}"
                    cache_key = hashlib.md5(cache_key.encode()).hexdigest()
                    cache_keys.append(f"{self.h1b_cache_prefix}{cache_key}")
                    original_keys.append(original_key)
                
                # Batch get from Redis
                cached_values = self.redis_client.mget(cache_keys)
                
                for i, value in enumerate(cached_values):
                    original_key = original_keys[i]
                    if value:
                        results[original_key] = float(value.decode())
                    else:
                        results[original_key] = None
            else:
                # Fallback cache
                for company, role in company_role_pairs:
                    original_key = f"{company}:{role}"
                    cache_key = f"{company.lower()}:{role.lower()}"
                    cache_key = hashlib.md5(cache_key.encode()).hexdigest()
                    
                    if cache_key in self._fallback_cache:
                        results[original_key] = self._fallback_cache[cache_key]['data']
                    else:
                        results[original_key] = None
            
            return results
            
        except Exception as e:
            print(f"Batch H1B cache get error: {e}")
            return {f"{company}:{role}": None for company, role in company_role_pairs}
    
    def batch_set_h1b_predictions(self, predictions: Dict[str, float], ttl: int = 86400) -> bool:
        """Batch set H1B predictions for better performance."""
        try:
            if self.redis_client:
                pipe = self.redis_client.pipeline()
                
                for company_role, prediction in predictions.items():
                    company, role = company_role.split(':', 1)
                    cache_key = f"{company.lower()}:{role.lower()}"
                    cache_key = hashlib.md5(cache_key.encode()).hexdigest()
                    pipe.setex(f"{self.h1b_cache_prefix}{cache_key}", ttl, str(prediction))
                
                pipe.execute()
                return True
            else:
                # Fallback cache
                for company_role, prediction in predictions.items():
                    company, role = company_role.split(':', 1)
                    cache_key = f"{company.lower()}:{role.lower()}"
                    cache_key = hashlib.md5(cache_key.encode()).hexdigest()
                    
                    self._fallback_cache[cache_key] = {
                        'data': prediction,
                        'expires_at': time.time() + ttl
                    }
                return True
                
        except Exception as e:
            print(f"Batch H1B cache set error: {e}")
            return False
    
    def invalidate_expired(self):
        """Clean up expired entries in fallback cache."""
        if not self.redis_client and hasattr(self, '_fallback_cache'):
            current_time = time.time()
            expired_keys = [
                key for key, value in self._fallback_cache.items()
                if value.get('expires_at', 0) < current_time
            ]
            for key in expired_keys:
                del self._fallback_cache[key]
    
    def get_status(self) -> Dict[str, Any]:
        """Get cache status and performance metrics."""
        try:
            status = {
                "connected": bool(self.redis_client),
                "hit_ratio": self._calculate_hit_ratio(),
                "total_requests": self.hit_count + self.miss_count,
                "cache_hits": self.hit_count,
                "cache_misses": self.miss_count
            }
            
            if self.redis_client:
                info = self.redis_client.info()
                status.update({
                    "memory_usage": info.get('used_memory_human', 'N/A'),
                    "connected_clients": info.get('connected_clients', 0),
                    "total_commands_processed": info.get('total_commands_processed', 0)
                })
            else:
                status.update({
                    "fallback_cache_size": len(getattr(self, '_fallback_cache', {})),
                    "memory_usage": "In-memory fallback"
                })
            
            return status
            
        except Exception as e:
            return {"error": str(e), "connected": False}
    
    def _calculate_hit_ratio(self) -> float:
        """Calculate cache hit ratio."""
        total_requests = self.hit_count + self.miss_count
        if total_requests == 0:
            return 0.0
        return (self.hit_count / total_requests) * 100
    
    def get_job_count(self) -> int:
        """Get total number of cached jobs."""
        try:
            if self.redis_client:
                return len(self.redis_client.keys(f"{self.job_cache_prefix}*"))
            else:
                return len([k for k in getattr(self, '_fallback_cache', {}) if k.startswith('jobs:')])
        except:
            return 0
    
    def get_hit_ratio(self) -> float:
        """Get cache hit ratio percentage."""
        return self._calculate_hit_ratio()
    
    def clear_cache(self, pattern: str = None) -> bool:
        """Clear cache entries matching pattern."""
        try:
            if self.redis_client:
                if pattern:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        return self.redis_client.delete(*keys) > 0
                else:
                    return self.redis_client.flushdb()
            else:
                if pattern:
                    keys_to_delete = [k for k in getattr(self, '_fallback_cache', {}) if pattern in k]
                    for key in keys_to_delete:
                        del self._fallback_cache[key]
                else:
                    self._fallback_cache.clear()
                return True
                
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False