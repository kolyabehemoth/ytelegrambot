from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from telegram_bot.entities.domain_entities import Singleton


# TODO: need to find real cache(not beaker), mb lru?
class CacheHandler(metaclass=Singleton):
    __cache_opts = {
        'cache_.type': 'file',
        'cache_.data_dir': '/tmp/cache_/data',
        'cache_.lock_dir': '/tmp/cache_/lock'
    }
    cache = None
    _cache_map = None

    def __init__(self):
        self.cache = CacheManager(**parse_cache_config_options(self.__cache_opts))
        self._cache_map = {}

    def get_data_by_telegram_bot_user_id(self, user_id):
        return self._cache_map[user_id] if user_id in self._cache_map else None
        #return self.cache.get_cache(user_id, type='dbm', expire=3600)

    def get_cache(self):
        pass
        #return self.cache

    #@cache.cache('', type="", expire=600)
    def put_data(self, user_id, data):
        self._cache_map[user_id] = data
        return self._cache_map[user_id]



