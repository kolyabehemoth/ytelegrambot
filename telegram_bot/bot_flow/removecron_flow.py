import logging
from telegram_bot.bot_flow.abstract_flow import AbstractFlow
from telegram_bot.entities.domain_entities import FlowTypes, DialogState

logger = logging.getLogger(__name__)


class RMCFlow(AbstractFlow):
    type = FlowTypes.REMOVE_CRON

    def __init__(self):
        super().__init__()

    def _flow(self, update, cache, user_id):
        logger.debug('REMOVE CRON FLOW')
        update.message.reply_text('Enter pls id of cron which you want to delete')

