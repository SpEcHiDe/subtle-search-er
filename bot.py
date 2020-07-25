#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os
import requests

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BASE_URL = "https://subtitle.iamidiotareyoutoo.com"
# this is required to avoid DuplicateCode


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hi!")


def echo(update, context):
    """Echo the user message."""
    input_text = update.message.text
    status_message = update.message.reply_text("🤔")

    request_url = f"{BASE_URL}/search/{input_text}/1"

    response = requests.get(request_url).json()
    print(response)

    response_data = response.get("r")
    if len(response_data) == 0:
        status_message.edit_text(
            text="no results obtained"
        )
        return

    inline_keyboard = []
    for a_response in response_data:
        inline_keyboard.append([InlineKeyboardButton(
            text=a_response.get("SIQ"),
            callback_data=a_response.get("DMCA_ID")
        )])

    status_message.edit_text(
        text="please select your required subtitle",
        reply_markup=InlineKeyboardMarkup(inline_keyboard)
    )


def button(update, context):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.message.edit_text("🤔")

    subtitle_id = query.data
    subtitle_get_url = f"{BASE_URL}/get/{subtitle_id}/"
    subtitle_response = requests.get(subtitle_get_url).json()

    subtitle_download_link = BASE_URL + subtitle_response.get("DL_LINK")
    subtitle_file_name = subtitle_response.get("DL_SUB_NAME")

    subtitle_file_response = requests.get(subtitle_download_link).content
    with open(subtitle_file_name, "wb") as f_d:
        f_d.write(subtitle_file_response)
    
    query.message.reply_document(
        document=open(subtitle_file_name, "rb"),
        caption=subtitle_file_name
    )

    # delete downloaded subtitle
    os.remove(subtitle_file_name)
    # delete the processing message
    query.message.delete()


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot"s token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1381874625:AAHFs-84jgFdsY0z51I8_kWIBxSssiV7jX8", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # on button click
    dp.add_handler(CallbackQueryHandler(button))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
