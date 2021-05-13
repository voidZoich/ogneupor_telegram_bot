import logging
import time

import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    Updater,
    CallbackContext,
    CallbackQueryHandler
)
from threading import Thread

from config import *
from ping import *
from users import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# State definitions for top level conversation
MAIN_MENU, SUBS, COMS, INFO, END, PING, BACK, START_OVER, SIGN = range(9)


# Top level conversation callbacks
def start(update: Update, context: CallbackContext) -> int:
    text = "Главное меню"
    buttons = [
        [
            InlineKeyboardButton(text='Подписки', callback_data=str(SUBS)),
            InlineKeyboardButton(text='Команды', callback_data=str(COMS)),
        ],
        [
            InlineKeyboardButton(text='Информация', callback_data=str(INFO)),
            InlineKeyboardButton(text='Выход', callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    if context.user_data.get(START_OVER):
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text(f"Здравствуйте, {update.effective_user.first_name}")
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False

    return MAIN_MENU


def subs(update: Update, context: CallbackContext) -> int:
    text = "Подписки"
    buttons = [
        [
            InlineKeyboardButton(text='Пинг', callback_data=str(PING)),
            InlineKeyboardButton(text='Назад', callback_data=str(BACK)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = True

    return SUBS


def coms(update: Update, context: CallbackContext) -> int:
    text = "Команды"
    buttons = [
        [
            InlineKeyboardButton(text='Пинг', callback_data=str(PING)),
            InlineKeyboardButton(text='Назад', callback_data=str(BACK)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = True

    return COMS


def info(update: Update, context: CallbackContext) -> int:
    pass


def stop(update: Update, _: CallbackContext) -> int:
    """End Conversation by command."""
    update.message.reply_text('До свидания!')

    return END


def end(update: Update, _: CallbackContext) -> int:
    """End conversation from InlineKeyboardButton."""
    update.callback_query.answer()

    text = 'До свидания!'
    update.callback_query.edit_message_text(text=text)

    return END


def cmd_ping(update: Update, _: CallbackContext) -> int:
    update.callback_query.edit_message_text("Начинаю опрос всех хостов, подождите минуту...")
    count = 0
    failed_hosts = list()
    for host_name in pinger():
        count += 1
        failed_hosts.append(host_name)
    if count > 0:
        text = "Эти хосты не пингуются: " + ", ".join(failed_hosts)
    else:
        text = "Все хосты пингуются нормально"
    update.callback_query.edit_message_text(text=text, reply_markup=update.effective_message.reply_markup)
    return COMS


def sub_ping(update: Update, context: CallbackContext) -> int:
    if context.user_data.get(PING) is True:
        text = "Отписаться"
    else:
        text = "Подписаться"

    buttons = [
        [
            InlineKeyboardButton(text=text, callback_data=str(SIGN)),
            InlineKeyboardButton(text='Назад', callback_data=str(BACK)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=f"{text} на ping?", reply_markup=keyboard)
    return SIGN


def sub_ping_toggle(update: Update, context: CallbackContext) -> int:
    if context.user_data.get(PING) is True:
        text = "Вы отписались от ping"
    else:
        text = "Вы подписались на ping"
    context.user_data[PING] = not context.user_data.get(PING)
    if context.user_data.get(PING) is True:
        button_text = "Отписаться"
    else:
        button_text = "Подписаться"

    buttons = [
        [
            InlineKeyboardButton(text=button_text, callback_data=str(SIGN)),
            InlineKeyboardButton(text='Назад', callback_data=str(BACK)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return SIGN


def ping_cycle():
    bot = telegram.Bot(TOKEN)
    while True:
        time.sleep(60)
        # bot.send_message(335449099, "Прошло 60 секунд")



def main() -> None:
    updater = Updater(token=TOKEN, workers=4)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(subs, pattern='^' + str(SUBS) + '$'),
                CallbackQueryHandler(coms, pattern='^' + str(COMS) + '$'),
                CallbackQueryHandler(info, pattern='^' + str(INFO) + '$')
            ],
            SUBS: [
                CallbackQueryHandler(sub_ping, pattern='^' + str(PING) + '$'),
                CallbackQueryHandler(start, pattern='^' + str(BACK) + '$'),
            ],
            SIGN: [
                CallbackQueryHandler(sub_ping_toggle, pattern='^' + str(SIGN) + '$'),
                CallbackQueryHandler(subs, pattern='^' + str(BACK) + '$'),
            ],
            COMS: [
                CallbackQueryHandler(cmd_ping, pattern='^' + str(PING) + '$'),
                CallbackQueryHandler(start, pattern='^' + str(BACK) + '$'),
            ],
            INFO: [],
        },
        fallbacks=[
            CommandHandler('stop', stop),
            CallbackQueryHandler(end, pattern='^' + str(END) + '$'),
        ],
        allow_reentry=True,
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    thread = Thread(target=ping_cycle)
    thread.start()
    main()
    thread.join()
