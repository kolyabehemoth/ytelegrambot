from telegram_bot.bot_flow.abstract_flow import AbstractFlow
from telegram_bot.entities.domain_entities import FlowTypes
from telegram_bot.dao.db_manager import CronsRepository
import re
import logging

logger = logging.getLogger(__name__)


class DSFlow(AbstractFlow):
    flow_type = FlowTypes.DISABLE_CRON
    cronRepository = CronsRepository()

    def __init__(self):
        super().__init__()

    def _flow(self, update, cache, user_id):
        logger.debug('Disable FLOW')
        user_id = update.message.from_user.id
        data = self.cache.get_data_by_telegram_bot_user_id(user_id)
        if data.flow_step == 0:
            update.message.reply_text('Enter pls id of cron which you want to disable')
            data.flow_step = 1
        elif data.flow_step == 1:
            cron_to_dis = self.parse_cron_id(update.message.text)
            cron = self.cronRepository.read_by_user_id(cron_to_dis)
            try:
                if not cron:
                    logger.info('no cron for user: %s with id: %s' % (str(user_id), update.message.text))
                    update.message.reply_text('Shit happened, can\'t find cron with such id')
                    return
                cron.active = False
                self.cronRepository.update(cron)
                update.message.reply_text('Updating cron was successful')
            except Exception:
                logger.error('Exception in Disable_flow happened')
                update.message.reply_text('Exception in Disable_flow happened')
            finally:
                data.flow_step = 0
                data.flow_ended = True

    def parse_cron_id(self, txt):
        for m in self._split_message(txt):
            if re.compile('\d{4}').match(m):
                return int(m)