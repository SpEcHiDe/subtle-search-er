#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
"""

import logging
import os
import requests
from io import BytesIO
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Updater,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    Filters
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

SUBTITLE_BASE_URL = os.environ.get("SUBTITLE_BASE_URL")
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
WEBHOOK = bool(os.environ.get("WEBHOOK", False))
PORT = int(os.environ.get("PORT", "1234"))
HEROKU_URL = os.environ.get("HEROKU_URL")
START_MESSAGE = os.environ.get("START_MESSAGE")
CHECKING_MESSAGE = os.environ.get("CHECKING_MESSAGE")
NO_SUBTITLE_AVAILABLE_MESSAGE = os.environ.get(
    "NO_SUBTITLE_AVAILABLE_MESSAGE"
)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text(START_MESSAGE)


def echo(update, context):
    """Echo the user message."""
    status_message = update.message.reply_text(CHECKING_MESSAGE)
    # logger.info(status_message)
    search_query = update.message.text

    request_url = f"{SUBTITLE_BASE_URL}/search/{search_query}/1"
    search_response = requests.get(request_url).json()
    # logger.info(search_response)

    search_response_arrey = search_response.get("r")

    if len(search_response_arrey) <= 0:
        status_message.edit_text(
            NO_SUBTITLE_AVAILABLE_MESSAGE
        )
        return

    ikeyboard = []
    for a_response in search_response_arrey:
        ikeyboard.append([InlineKeyboardButton(
            text=a_response.get("SIQ"),
            callback_data=a_response.get("DMCA_ID")
        )])

    status_message.edit_text(
        text="please select your required subtitle",
        reply_markup=InlineKeyboardMarkup(ikeyboard)
    )


def button(update, context):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    subtitle_id = query.data

    query.edit_message_text(CHECKING_MESSAGE)

    request_url = f"{SUBTITLE_BASE_URL}/get/{subtitle_id}/"
    download_link_response = requests.get(request_url).json()

    DL_LINK = SUBTITLE_BASE_URL + download_link_response.get("DL_LINK")
    DL_SUB_NAME = download_link_response.get("DL_SUB_NAME")

    download_content = BytesIO(requests.get(DL_LINK).content)
    # https://stackoverflow.com/a/42811024
    download_content.name = DL_SUB_NAME
    query.message.reply_document(
        document=download_content,
        caption=download_link_response.get("DL_LANGUAGE")
    )

    query.message.delete()


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot"s token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(
        TG_BOT_TOKEN,
        use_context=True
    )

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # on clicking a button
    dp.add_handler(CallbackQueryHandler(button))

    # Start the Bot
    if WEBHOOK:
        logger.info("using WEBHOOKs")
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TG_BOT_TOKEN
        )
        # https://t.me/MarieOT/22915
        updater.bot.set_webhook(url=HEROKU_URL + Config.TG_BOT_TOKEN)
    else:
        logger.info("using Long Polling")
        updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
