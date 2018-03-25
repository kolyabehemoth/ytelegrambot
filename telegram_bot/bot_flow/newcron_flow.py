import logging

from telegram_bot.bot_flow.abstract_flow import AbstractFlow
from telegram_bot.entities.domain_entities import FlowTypes, ReportParams, CException
from telegram_bot.entities.db_entities import Cron
from telegram_bot.dao.db_manager import CronsRepository
from telegram_bot.validators import Validator

logger = logging.getLogger(__name__)


class NCFlow(AbstractFlow):
    flow_type = FlowTypes.NEW_CRON
    cronRepository = CronsRepository()
    validators = Validator.__subclasses__()

    def __init__(self):
        super().__init__()

    def _flow(self, update, cache, user_id):
        logger.debug('NEWCRON FLOW')
        self.steps[cache.flow_step](self, update, cache, user_id)

    def step_0(self, update, cache, user_id):
        update.message.reply_text('New cron yeahhhh.')
        update.message.reply_text('Enter pls params split by comma, in brackets default value, + required params')
        update.message.reply_text('+cron_name, +cron_start_string, +account_id, start_date(today-1d), end_date(today), '
                                  'currency($), dimension(AD_UNIT_ID), filter(), locale(en_US), metric(earnings), sort()')
        cache.flow_step = 1

    def step_1(self, update, cache, user_id):
        try:
            params, msgs = self.parse_params(update.message.text)
            if msgs:
                raise CException(msgs)
            rp = ReportParams(**params)
            cron = Cron(**params)
            cron.request_params = rp
            self.cronRepository.create(cron, user_id)
            update.message.reply_text('Cron has been created')
            cache.flow_step = 0
            cache.flow_ended = True
        except CException as e:
            update.message.reply_text(e)

    def parse_params(self, txt):
        p = txt.split(',') if txt else []
        if len(p) < 3:
            raise CException('You miss some required parameters(cron_name, cron_start_string, adsense_account_id)')
        params_dict = {}
        msgs = []
        for i in range(0, len(p)):
            try:
                pval = p[i].strip()
                validator = self.validators[i]()
                logger.debug('validator: ' + str(validator) + ' value: ' + pval)
                key, val = validator.validate(pval)
                params_dict[key] = val
            except CException as e:
                msgs.append(e)
        return params_dict, msgs

    steps = {
        0: step_0,
        1: step_1,
    }
