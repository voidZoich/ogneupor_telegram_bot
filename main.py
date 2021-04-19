import logging

import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
    Updater
)

from config import *
from ping import *
from users import *

updater = Updater(token=TOKEN, workers=4)
bot = telegram.Bot(TOKEN)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

REGISTER, MENU, PING = range(3)
ADMIN_REGISTER, SELECT_ROLE = range(2)
new_user = list


def start(update, context):
    user = update.effective_user

    if isregistered(user.id):
        message = f"Здравствуйте, {user.first_name}"
        reply_keyboard = [every_command(user.id)]
        next_step = MENU
    else:
        message = "Вы должны пройти регистрацию"
        reply_keyboard = [['Регистрация', 'Отмена']]
        next_step = REGISTER

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return next_step


def register(update, context) -> int:
    user = update.effective_user
    global new_user
    new_user = user.id, user.full_name, user.username
    for id in every_user_id('admin'):
        message = f'Зарегистрировать пользователя "{user.full_name}" ({user.username})?'
        reply_keyboard = [['Зарегистрировать', 'Отмена']]
        context.bot.send_message(
            chat_id=id,
            text=message,
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
    return ConversationHandler.END


def admin_register(update, context) -> int:
    message = 'Выберите роль нового пользователя'
    reply_keyboard = [every_role()]
    update.message.reply_text(
        text=message,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return SELECT_ROLE


def select_role(update, context) -> int:
    role = update.effective_message.text
    update.message.reply_text(f'Пользователь {new_user[1]} зарегистрирован как {role}', reply_markup=ReplyKeyboardRemove())
    register_user(*new_user, role)
    return ConversationHandler.END


def menu(update, context):
    pass


def ping(update, _):
    for host_name, time in pinger():
        emoji = '❌' if time is None else '✅'
        update.message.reply_text(
            f"{emoji} {host_name} - {time} сек.",
            reply_markup=ReplyKeyboardRemove()
        )


def cancel(update, _) -> int:
    user = update.message.from_user
    logging.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'До свидания!', reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Неизвестная команда")


def main():
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            REGISTER: [MessageHandler(Filters.regex('^(Регистрация|регистрация)$'), register)],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            MessageHandler(Filters.regex('^(Отмена|отмена)$'), cancel)
        ],
    )
    dispatcher.add_handler(conv_handler)

    admin_register_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^(Зарегистрировать|зарегистрировать)$'), admin_register)],
        states={
            SELECT_ROLE: [MessageHandler(Filters.text, select_role)],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            MessageHandler(Filters.regex('^(Отмена|отмена)$'), cancel)
        ],
    )
    dispatcher.add_handler(admin_register_handler)

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    register_handler = MessageHandler(Filters.regex('^(Регистрация|регистрация)$'), register)
    dispatcher.add_handler(register_handler)

    ping_handler = MessageHandler(Filters.regex('^(Пинг|пинг|Ping|ping)$'), ping)
    dispatcher.add_handler(ping_handler)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
