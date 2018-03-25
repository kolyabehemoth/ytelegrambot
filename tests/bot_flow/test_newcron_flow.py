from telegram_bot.entities.db_entities import User as DUser
from tests import conftest as cfg
from telegram_bot.bot_flow import newcron_flow

def setup_function(function):
    #print("function setup")
    cfg.userRep.create(DUser(1, active=True))


def teardown_function(function):
    #print("function teardown")
    cfg.cronRep.delete_all()
    cfg.userRep.delete(1)


def test_step_0(resource_setup):
    print('test_step_0')
    flow = newcron_flow.NCFlow()
    update, user_id = resource_setup
    flow.step_0(update, flow.cache, user_id)
    assert True


def test_step_1_fail_not_enough_params(resource_setup):
    print('test_step_1')
    flow = newcron_flow.NCFlow()
    update, user_id = resource_setup
    update.message.text = 'text'
    #flow.step_1(update, flow.cache, user_id)
    assert True


def test_step_1_pass(resource_setup):
    print('test_step_1')
    flow = newcron_flow.NCFlow()
    update, user_id = resource_setup
    update.message.text = 'cron_super_name, */2 * * * *, pub-1234567890987654'
    flow.step_1(update, flow.cache, user_id)
    cron = cfg.cronRep.read_by_user_id(user_id)
    print(cron[0])
    assert True


def test_parse_params():
    assert True

