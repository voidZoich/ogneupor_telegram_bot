import logging
from config import *
from ping import *

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

updater = Updater(token=TOKEN, workers=4)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(update, context):
    reply_keyboard = [['Пинг']]
    update.message.reply_text(
        'Здравствуйте, я бот АСУ ТП Огнеупор, введите команду',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True),
    )


def ping(update, context):
    for host_name, time in pinger():
        emoji = '❌' if time is None else '✅'
        update.message.reply_text(
            f"{emoji} {host_name} - {time} сек.",
            reply_markup=ReplyKeyboardRemove()
        )


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Неизвестная команда")


def main():
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    ping_handler = MessageHandler(Filters.regex('^(Пинг|пинг|Ping|ping)$'), ping)
    dispatcher.add_handler(ping_handler)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
