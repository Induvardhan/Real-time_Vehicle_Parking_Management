"""
Redis Configuration for ParkEase
Handles Redis connections for caching and Celery message broker
"""

import os
import redis
from flask_caching import Cache

# Redis connection settings
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

# Redis URLs for different purposes
REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}" if REDIS_PASSWORD else f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
CELERY_BROKER_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/1" if REDIS_PASSWORD else f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
CELERY_RESULT_BACKEND = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/2" if REDIS_PASSWORD else f"redis://{REDIS_HOST}:{REDIS_PORT}/2"

# Flask-Caching configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': REDIS_DB,
    'CACHE_REDIS_PASSWORD': REDIS_PASSWORD,
    'CACHE_DEFAULT_TIMEOUT': 300,  # 5 minutes default
    'CACHE_KEY_PREFIX': 'parkeasy_'
}

# Create Redis client
def get_redis_client():
    """Get Redis client instance"""
    try:
        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        # Test connection
        client.ping()
        return client
    except redis.ConnectionError as e:
        print(f"Redis connection failed: {e}")
        return None
    except Exception as e:
        print(f"Redis client error: {e}")
        return None

# Initialize cache (will be configured in main app)
cache = Cache()

# Global Redis client instance
redis_client = None

def init_redis(app):
    """Initialize Redis connection and Flask-Caching"""
    global redis_client
    
    try:
        # Configure Flask-Caching
        app.config.update(CACHE_CONFIG)
        cache.init_app(app)
        
        # Initialize Redis client
        redis_client = get_redis_client()
        
        if redis_client:
            print("✅ Redis initialized successfully")
            return True
        else:
            print("⚠️ Redis initialization failed - using database fallback")
            return False
            
    except Exception as e:
        print(f"❌ Redis initialization error: {e}")
        print("📝 Running with database fallback")
        return False

# Initialize redis_client on import for backward compatibility
redis_client = get_redis_client()
