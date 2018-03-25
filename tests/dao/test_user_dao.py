from telegram_bot.entities.db_entities import User as User
from tests import conftest as cfg

user_id = 1


def setup_function(function):
    print("function setup")


def teardown_function(function):
    print("function teardown")
    cfg.userRep.delete(user_id)


def test_create():
    user = User(user_id, active=True, chat_id=123456)
    cfg.userRep.create(user)
    db_user = cfg.userRep.read_by_id(user_id)
    assert db_user.id == user.id


def test_update():
    chat_id = 123456
    user = User(user_id, active=True, chat_id=chat_id)
    cfg.userRep.create(user)
    r_user = cfg.userRep.read_by_id(user_id)
    assert r_user.chat_id == chat_id
    n_chat_id = 18
    r_user.chat_id = n_chat_id
    cfg.userRep.update(r_user)
    n_user = cfg.userRep.read_by_id(user_id)
    assert n_user.chat_id != user.chat_id
    assert n_user.chat_id == n_chat_id
