from telegram_bot.entities.db_entities import User as DUser, Cron
from telegram_bot.entities.domain_entities import ReportParams
from tests import conftest as cfg
from telegram_bot.bot_flow import next_run_flow


def setup_function(function):
    print("function setup")
    cfg.userRep.create(DUser(1, active=True))
    rp = ReportParams(**{'account_id': 'pub-1234567890987654'})
    cron = Cron(**{'name':'cronYname', 'request_params': rp})
    cfg.cronRep.create(cron, 1)



def teardown_function(function):
    #print("function teardown")
    cfg.cronRep.delete_all()
    cfg.userRep.delete(1)


def test_next_run_flow_pass(resource_setup):
    print('next run flow')
    flow = next_run_flow.NRFlow()
    update, user_id = resource_setup
    flow.flow(update)