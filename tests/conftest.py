import pytest
from telegram.bot import Bot
from telegram.utils.request import Request

from telegram_bot.config_bot import MyWebhookServer
from telegram_bot.dao.db_manager import CronsRepository, UserRepository
from datetime import datetime
from telegram.update import Update, Message
from telegram.user import User
from telegram.chat import Chat


userRep = UserRepository()
cronRep = CronsRepository()


@pytest.fixture(scope='function')
def resource_setup(request):
    user_id = 1
    user = User(user_id, 'haha', False)
    chat = Chat(13, Chat.PRIVATE)
    bot = MockedBot('very token')
    msg = Message(2, user, datetime.now(), chat, bot=bot)
    update = Update(1266, message=msg)
    return update, user_id


class MockedBot(Bot):

    def __init__(self, token, base_url=None, base_file_url=None, request=None):
        super().__init__(token, base_url=base_url, base_file_url=base_file_url, request=request)
        self._request = request or MockedRequest()

    @staticmethod
    def _validate_token(token):
        return token


class MockedRequest(Request):

    def __init__(self, con_pool_size=1, proxy_url=None, urllib3_proxy_kwargs=None, connect_timeout=5., read_timeout=5.):
        super().__init__(con_pool_size, proxy_url, urllib3_proxy_kwargs, connect_timeout, read_timeout)

    def get(self, url, timeout=None):
        print(url)

    def post(self, url, data, timeout=None):
        print(data)


class MockedServer(MyWebhookServer):

    def __init__(self, update_queue, bot):
        super().__init__(('localhost', 8080),  update_queue, 'path', bot)

    def handle_request(self):
       print('mocked_server handle_request')

    def set_query_params_resp(self, data):
        self.query_params = data
