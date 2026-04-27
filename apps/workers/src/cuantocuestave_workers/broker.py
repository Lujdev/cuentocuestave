import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import Retries

from cuantocuestave_infra.settings import Settings

settings = Settings()

broker = RedisBroker(url=settings.redis_url)
broker.add_middleware(Retries(max_retries=3, min_backoff=5000, max_backoff=300000))

dramatiq.set_broker(broker)
