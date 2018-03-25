from telegram_bot.entities.db_entities import User as DUser
from telegram_bot.entities.db_entities import Cron
from telegram_bot.entities.domain_entities import ReportParams
from telegram_bot.bot_flow import availablecrons_flow
from tests import conftest as cfg


def setup_function(function):
    print("function setup")
    cfg.userRep.create(DUser(1, active=True))
    rp = ReportParams(**{'account_id': 'pub-1234567890987654'})
    cron = Cron(**{'name':'cronYname', 'request_params': rp})
    cfg.cronRep.create(cron, 1)


def teardown_function(function):
    print("function teardown")
    cfg.cronRep.delete_all()
    cfg.userRep.delete(1)


def test_flow_pass(resource_setup):
    print('test available_crons_flow')
    flow = availablecrons_flow.AFlow()
    update, user_id = resource_setup
    flow.flow(update)
    print('clap')
