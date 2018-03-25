import json
import logging
from googleapiclient.errors import HttpError
from telegram_bot.bot_flow.abstract_flow import AbstractFlow
from telegram_bot.entities import domain_entities
from telegram_bot.entities.domain_entities import FlowTypes, CException
from telegram_bot.adsense_api.api import AdSenseAPIClientv2
from telegram_bot.validators import AccountIdValidator

logger = logging.getLogger(__name__)


class DFlow(AbstractFlow):
    flow_type = FlowTypes.DEFAULT
    account_id_validator = AccountIdValidator()

    def __init__(self):
        super().__init__()

    def _flow(self, update, cache, user_id):
        logger.debug('DEFAULT_FLOW')
        try:
            client = AdSenseAPIClientv2(update.message.reply_text, user_id)
        except CException as e:
            update.message.reply_text(e)
            return
        try:
            fn, id = self.account_id_validator.validate(message=update.message.text)
            report = client.get_default_report(id)
            if not report:
                update.message.reply_text('No data in report')
                return
            update.message.reply_text(domain_entities.format_report(report))
            logger.debug('got report')
        except CException as ce:
            logger.error('exception happened: %s' % str(ce))
            update.message.reply_text(ce)
        except HttpError as he:
            logger.error('http error: %s' % str(he))
            error = json.loads(str(he.content, 'utf-8')).get('error')
            if error:
                update.message.reply_text('Google error response: %s' % error['message'])
            else:
                update.message.reply_text('Internal error')
        finally:
            cache.flow_ended = True
            cache.flow_step = 0
