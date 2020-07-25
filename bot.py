#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of 'subtle-search-er'.
# This is free software:
# you can redistribute it and/or modify it
# under the terms of the GNU General Public License
# as published by the Free Software Foundation,
# either version 3 of the License,
# or (at your option) any later version.
#
# 'subtle-search-er' is distributed in the hope
# that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.
#
# See the GNU General Public License for more details.
# You should have received a copy of the
# GNU General Public License along with 'subtle-search-er'.
# If not, see <http://www.gnu.org/licenses/>.

"""
Simple Bot to reply to Telegram messages.
"""

import logging
import os
from io import BytesIO
import requests
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

__author__ = "Shrimadhav U K <https://t.me/SpEcHlDe>"
__copyright__ = "2020-2020 Shrimadhav U K <https://t.me/SpEcHlDe>"
__license__ = "https://opensource.org/licenses/GPL-3.0 GPLv3"


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
LOGGER = logging.getLogger(__name__)

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
ASK_FOR_SUBTITLE_B_TEXT = os.environ.get(
    "ASK_FOR_SUBTITLE_B_TEXT"
)


# Define a few command handlers.
# These usually take the two arguments update and context.
# Error handlers also receive the raised TelegramError object in error.
def start(update, _):
    """Send a message when the command /start is issued."""
    update.message.reply_text(START_MESSAGE)


def echo(update, _):
    """Echo the user message."""
    status_message = update.message.reply_text(CHECKING_MESSAGE)
    # LOGGER.info(status_message)
    search_query = update.message.text

    request_url = f"{SUBTITLE_BASE_URL}/search/{search_query}/1"
    search_response = requests.get(request_url).json()
    # LOGGER.info(search_response)

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
        text=ASK_FOR_SUBTITLE_B_TEXT,
        reply_markup=InlineKeyboardMarkup(ikeyboard)
    )


def button(update, _):
    """ handle the button clicks """
    query = update.callback_query

    # CallbackQueries need to be answered,
    # even if no notification to the user is needed
    # Some clients may have trouble otherwise.
    # See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    subtitle_id = query.data

    query.edit_message_text(CHECKING_MESSAGE)

    request_url = f"{SUBTITLE_BASE_URL}/get/{subtitle_id}/"
    download_link_response = requests.get(request_url).json()

    download_link = SUBTITLE_BASE_URL + download_link_response.get("DL_LINK")
    downloaded_file_name = download_link_response.get("DL_SUB_NAME")

    download_content = BytesIO(requests.get(download_link).content)
    # https://stackoverflow.com/a/42811024
    download_content.name = downloaded_file_name
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

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler("start", start))

    # on noncommand i.e message - echo the message on Telegram
    updater.dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command,
        echo
    ))

    # on clicking a button
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    # Start the Bot
    if WEBHOOK:
        LOGGER.info("using WEBHOOKs")
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TG_BOT_TOKEN
        )
        # https://t.me/c/1186975633/22915
        updater.bot.set_webhook(url=HEROKU_URL + TG_BOT_TOKEN)
    else:
        LOGGER.info("using Long Polling")
        updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
