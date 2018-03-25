from http.client import HTTPResponse
import os
import httplib2
import pytest
from telegram_bot.entities.domain_entities import ReportParams
from tests import conftest as cfg
from telegram_bot import scheduler
from telegram_bot.entities.db_entities import User, Cron
from telegram_bot import bot_main
from queue import Queue
from six.moves import http_client


def setup_function(function):
    user1 = User(1, active=False, chat_id=2211)
    user2 = User(2, active=True, chat_id=322)
    cfg.userRep.create(user1)
    cfg.userRep.create(user2)
    cron1_1 = Cron(**{'name': 'cron1', 'cron_string': '* * * * *', 'active': True, 'request_params': ReportParams(**{'account_id':144})})
    cron1_2 = Cron(**{'name': 'cron2', 'cron_string': '*/2 * * * *', 'active': False, 'request_params': ReportParams(**{'account_id':144})})
    cron2_1 = Cron(**{'name': 'cron3', 'cron_string': '* */2 * * *', 'active': True, 'request_params': ReportParams(**{'account_id':154})})
    cron2_2 = Cron(**{'name': 'cron4', 'cron_string': '*/10 * * * *', 'active': True, 'request_params': ReportParams(**{'account_id':154})})
    cfg.cronRep.create(cron1_1, user_id=user1.id)
    cfg.cronRep.create(cron1_2, user_id=user1.id)
    cfg.cronRep.create(cron2_1, user_id=user2.id)
    cfg.cronRep.create(cron2_2, user_id=user2.id)
    print("function setup")


def teardown_function(function):
    print("function teardown")
    cfg.cronRep.delete_all()
    cfg.userRep.delete(1)
    cfg.userRep.delete(2)


@pytest.fixture(scope='function')
def config_bot_fixture(resource_setup):
    update, id = resource_setup
    bot_main.bot = update.message.bot
    queue = Queue()
    bot_main.webserver = cfg.MockedServer(queue, bot_main.bot)


def mocked_request(http, uri, method='GET', body=None, headers=None, redirections=httplib2.DEFAULT_MAX_REDIRECTS,
                   connection_type=None):
    print('mocked transport shit')
    resp = CHTTPResponse()
    resp.status = http_client.OK
    f_loc = os.path.join(os.path.dirname(__file__), 'adsense_api/adsense_service_schema.json')
    with open(f_loc) as f:
        data = f.read()
    content = '{"access_token": "so token omg", ' + data[1:]
    return resp, content


def test_cron_job_starter_functionality(config_bot_fixture, resource_setup):
    data = {'code': '4/AADkl4Xsecgr9x-NyjYKrafPoja-usy9n3SgfohbvM8f-T4NFgrl19QcO6Cr6SVIZERRokns3SiphHQ5d5Q-joE'}
    bot_main.webserver.set_query_params_resp(data)
    from oauth2client import transport
    transport.request = mocked_request  # SOOO SMART
    scheduler.timed_cron_job()


    # with requests_mock.Mocker() as mock:
    #     mock.post('https://accounts.google.com/o/oauth2/token', text='resp')
    #     p = requests.post(url='https://accounts.google.com/o/oauth2/token', data='{}')


class CHTTPResponse(HTTPResponse):

    def __init__(self):
        pass
