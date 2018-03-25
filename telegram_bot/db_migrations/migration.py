from telegram_bot import config
from pyquibase.pyquibase import Pyquibase


def migrate():
    db_conf = config.global_config.db_url
    pyquibase = Pyquibase.postgresql(
        host=db_conf.hostname,
        port=db_conf.port,
        db_name=db_conf.database,
        username=db_conf.username,
        password=db_conf.password,
        change_log_file='./telegram_bot/db_migrations/changelog.xml',
        log_file='out.log',
        log_level='debug'
    )
    pyquibase.update()
