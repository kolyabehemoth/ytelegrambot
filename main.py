from telegram_bot import bot_main
from telegram_bot import scheduler
from telegram_bot.db_migrations import migration
import logging
import sys
import warnings


def config_logger():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)


if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    config_logger()
    migration.migrate()
    scheduler.main()
    bot_main.main()
