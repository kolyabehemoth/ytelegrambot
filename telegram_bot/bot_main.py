from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram_bot import config
import os
import logging
from telegram_bot.cache_.m_cache import CacheHandler
from telegram_bot.config_bot import MyUpdater
from telegram_bot.dao.db_manager import UserRepository
from telegram_bot.entities.db_entities import User
from telegram_bot.bot_flow import default_flow, newcron_flow, removecron_flow, availablecrons_flow, disable_flow, enable_flow, next_run_flow
from telegram_bot.entities.domain_entities import FlowTypes

PORT = int(os.environ.get('PORT', '8443'))
logger = logging.getLogger(__name__)

userRepository = UserRepository()
cache = CacheHandler()
webserver = None
bot = None

flows = {
    FlowTypes.DEFAULT: default_flow.DFlow(),
    FlowTypes.AVAILABLE_CRONS: availablecrons_flow.AFlow(),
    FlowTypes.NEW_CRON: newcron_flow.NCFlow(),
    FlowTypes.REMOVE_CRON: removecron_flow.RMCFlow(),
    FlowTypes.DISABLE_CRON: disable_flow.DSFlow(),
    FlowTypes.ENABLE_CRON: enable_flow.EFlow(),
    FlowTypes.NEXT_RUN: next_run_flow.NRFlow()
}


def start(bot, update):
    """Send a message when the command /start is issued."""
    user = userRepository.read_by_id(update.message.from_user.id)
    if not user:
        userRepository.create(User(update.message.from_user.id, active=True, chat_id=update.message.chat.id))
    update.message.reply_text('Hi!')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        'It\'s a fucking help!\n '
        'This shitty bot can make reports and send you it in the targeting time, with selected info/fields\n'
        'For usage you can just write AdSense account_id and get report with earning stats for last day\n'
        '\n'
        'Available Commands:\n'
        '/newcron --- create new \n'
        '/avacrons --- view existing crons \n'
        '/discron --- disable selected cron \n'
        '/rmcron --- remove cron by name \n'
        '/nextrun --- next cron run\n'
        '\n'
    )


def new_cron(bot, update):
    flows[FlowTypes.NEW_CRON].flow(update)


def ava_crons(bot, update):
    flows[FlowTypes.AVAILABLE_CRONS].flow(update)


def rm_cron(bot, update):
    flows[FlowTypes.REMOVE_CRON].flow(update)


def dis_cron(bot, update):
    flows[FlowTypes.DISABLE_CRON].flow(update)


def en_cron(bot, update):
    flows[FlowTypes.ENABLE_CRON].flow(update)


def next_cron_run(bot, update):
    flows[FlowTypes.NEXT_RUN].flow(update)


def message_handler(bot, update):
    user_cache = cache.get_data_by_telegram_bot_user_id(update.message.from_user.id)
    if not user_cache or user_cache.flow_ended:
        user = userRepository.read_by_id_vs_cache(update.message.from_user.id)
        if not user:
            update.message.reply_text('Enter /start for use this bot')
            return
        # temporary for migration
        if not user.chat_id:
            user.chat_id = update.message.chat.id
            userRepository.update(user)
        user_cached_flow = flows[FlowTypes.DEFAULT]
    else:
        user_cached_flow = flows[user_cache.flow_type]
    user_cached_flow.flow(update)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    logger.debug('BOT MAIN')
    updater = MyUpdater(config.global_config.telegram_token)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("newcron", new_cron))
    dp.add_handler(CommandHandler("avacrons", ava_crons))
    dp.add_handler(CommandHandler("rmcron", rm_cron))
    dp.add_handler(CommandHandler("discron", dis_cron))
    dp.add_handler(CommandHandler("encron", en_cron))
    dp.add_handler(CommandHandler("nextrun", next_cron_run))

    dp.add_handler(MessageHandler(Filters.text, message_handler))

    dp.add_error_handler(error)
    logger.info('PORT HAS CHOOSE ONE: ' + str(PORT))
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=config.global_config.telegram_token)
    updater.bot.set_webhook(config.global_config.web_host + '/' + config.global_config.telegram_token)
    global webserver
    webserver = updater.httpd
    global bot
    bot = updater.bot
    logger.info('webserver: %s' % str(webserver))
    updater.idle()
