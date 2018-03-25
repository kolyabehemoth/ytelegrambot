from telegram_bot.bot_flow.abstract_flow import AbstractFlow
from telegram_bot.entities.domain_entities import FlowTypes
from telegram_bot.dao.db_manager import UserRepository, CronsRepository
import logging

logger = logging.getLogger(__name__)


class AFlow(AbstractFlow):
    flow_type = FlowTypes.AVAILABLE_CRONS
    userRepository = UserRepository()
    cronRepository = CronsRepository()

    def __init__(self):
        super().__init__()

    def _flow(self, update, cache, user_id):
        logger.debug('Available Flow')
        crons = self.cronRepository.read_by_user_id(user_id)
        if not crons:
            logger.debug('for user %s cron list is empty' % str(user_id))
            update.message.reply_text('Your crons list is empty')
        else:
            logger.debug('Crons for user: %s : [%s]' % (str(user_id), crons))
            for cron in crons:
                update.message.reply_text(cron.format())
        #data = self.cache.get_data_by_telegram_bot_user_id(user_id)
        cache.flow_ended = True
        cache.flow_step = 0
