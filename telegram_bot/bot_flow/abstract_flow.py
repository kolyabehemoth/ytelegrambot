import abc
from telegram_bot.entities.domain_entities import ReportParams
from telegram_bot.cache_.m_cache import CacheHandler
from telegram_bot.entities.domain_entities import DialogState
import re
import logging

logger = logging.getLogger(__name__)


class AbstractFlow(object, metaclass=abc.ABCMeta):
    rp_acc = re.compile('pub-\d{16}')
    rp_adc = re.compile('ca-pub-\d{6}')
    rp_adu = re.compile('ca-pub-\d{6}:\d{6}')

    def __init__(self):
        self.cache = CacheHandler()

    def flow(self, update):
        user_id = update.message.from_user.id
        u_cache = self.cache.get_data_by_telegram_bot_user_id(user_id)
        if not u_cache or u_cache.flow_type != self.flow_type or u_cache.flow_ended:
            u_cache = self.cache.put_data(user_id, DialogState(user_id, self.flow_type))
        logger.info('XXX cache: %s,,, user_id: %s' % (str(u_cache), str(user_id)))
        self._flow(update,  u_cache, user_id)

    @abc.abstractmethod
    def _flow(self, update, cache, user_id):
        raise NotImplementedError('You should implement flow method to use this class')

    @staticmethod
    def _split_message(message):
        return message.split(' ') if message else []

    def is_flow_ended(self, user_id):
        data = self.cache.get_data_by_telegram_bot_user_id(user_id)
        return data.flow_ended

    @staticmethod
    def _match(msgs):
        report_params = ReportParams()
        for msg in msgs:
            if AbstractFlow.rp_acc.match(msg):
                report_params.account_id = msg
        return report_params