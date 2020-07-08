<?php
/**
 * the main webhook
 *
 * This file is part of 'subtle-search-er'.
 * This is free software:
 * you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
 * 'subtle-search-er' is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License along with 'subtle-search-er'.
 * If not, see <http://www.gnu.org/licenses/>.
 *
 * @author    Shrimadhav U K <https://t.me/SpEcHlDe>
 * @copyright 2020-2020 Shrimadhav U K <https://t.me/SpEcHlDe>
 * @license   https://opensource.org/licenses/GPL-3.0 GPLv3
 *
 */

require_once __DIR__ . "/config.php";
use kyle2142\PHPBot;

// set the bot TOKEN
$bot_id = $GLOBALS["TG_BOT_TOKEN"];
// initialize the Telegram Bot Object
$bot = new PHPBot($bot_id);
// get the Telegram webhook payload
$content = file_get_contents("php://input");
// JSONify the received payload
$update = json_decode($content, true);

// triggers to be handled when a message is received
if (isset($update["message"])) {
    $message_id = $update["message"]["message_id"];
    $chat_id = $update["message"]["chat"]["id"];
    $chat_type = $update["message"]["chat"]["type"];

    if (
        ($chat_type == "group") ||
        ($chat_type == "supergroup")
    ) {
        try {
            $bot->api->leaveChat(array(
                "chat_id" => $chat_id
            ));
        }
        catch (Exception $e) {
        }
        // return something to
        // pre-emptively exit from the script
        return FALSE;
    }

    // if we receive a message in PM
    if (isset($update["message"]["text"])) {
        $message_text = $update["message"]["text"];

        if (strpos($message_text, "/") !== FALSE) {
            $bot->api->sendMessage(array(
                "chat_id" => $chat_id,
                "text" => $GLOBALS["START_MESSAGE"],
                "parse_mode" => "HTML",
                "disable_notification" => True,
                "reply_to_message_id" => $message_id
            ));
        }

        else {
            // send a status message to edit the response,
            // as required
            $status_message = $bot->api->sendMessage(array(
                "chat_id" => $chat_id,
                "text" => $GLOBALS["CHECKING_MESSAGE"],
                "parse_mode" => "HTML",
                "disable_notification" => True,
                "reply_to_message_id" => $message_id
            ));

            // search subtitles using the API
            $reply_markup = search_srt_a(
                $message_text,
                1
            );

            if ($reply_markup !== NULL) {
                // edit the previously sent message,
                // with the buttons
                $bot->api->editMessageText(array(
                    "chat_id" => $chat_id,
                    "message_id" => $status_message->message_id,
                    "text" => $GLOBALS["MESG_DETIDE"],
                    "parse_mode" => "HTML",
                    "disable_web_page_preview" => True,
                    "reply_markup" => $reply_markup
                ));
            }

            else {
                // answer back saying search is not found
                $bot->api->editMessageText(array(
                    "chat_id" => $chat_id,
                    "message_id" => $status_message->message_id,
                    "text" => $GLOBALS["GESM_ITEDED"],
                    "parse_mode" => "HTML",
                    "disable_web_page_preview" => True
                ));
            }
        }
    }
}


// triggers to be handled when a message is received,
// from a channel :\
if (isset($update["channel_post"])) {
    try {
        $bot->api->leaveChat(array(
            "chat_id" => $update["channel_post"]["chat"]["id"]
        ));
    }
    catch (Exception $e) {
    }
}


// triggers to be handled when a button is pressed
// 'should' happen only in PRIVATE chats,
// but we never know :\
if (isset($update["callback_query"])) {
    $callback_query = $update["callback_query"];
    $id = $callback_query["id"];
    $message_from_user = $callback_query["from"];
    $chat_id = $callback_query["from"]["id"];
    $message = $callback_query["message"];
    $cb_data = $callback_query["data"];
    $message_id = $message["message_id"];

    // NOTE: You should always answer,
    // but we want different conditionals to
    // be able to answer to differnetly
    // (and we can only answer once),
    // so we don't always answer here.
    $bot->api->answerCallbackQuery(array(
        "callback_query_id" => $id
    ));

    // edit the previously sent message,
    // to avoid the repeated clicking of buttons
    $bot->api->editMessageText(array(
        "chat_id" => $chat_id,
        "message_id" => $message_id,
        "text" => $GLOBALS["ANSWERING_MESSAGE"],
        "parse_mode" => "HTML",
        "disable_web_page_preview" => True
    ));

    // if the button containing,
    // a particular file was clicked
    if (strpos($cb_data, "dl_") !== FALSE) {
        // extract subtitle ID from the callback
        $sub_id = explode("_", $cb_data)[1];

        // get the subtitle to send
        $sub_doc_params = get_sub_i($sub_id, $chat_id);
        $sub_doc_params["reply_to_message_id"] = $message_id;

        // call the API, to send the DOCument
        $bot->api->sendDocument($sub_doc_params);

        // delete the SENT document
        @unlink($sub_doc_params["document"]);

        $bot->api->deleteMessage(array(
            "chat_id" => $chat_id,
            "message_id" => $message_id
        ));
    }

    // if the button containing,
    // Next or Previous buttons were clicked
    else if (strpos($cb_data, "page_") !== FALSE) {
        // extract required page number from the callback
        $page_no = explode("_", $cb_data)[1];

        $message_text = $message["reply_to_message"]["text"];

        // search subtitles using the API
        $reply_markup = search_srt_a(
            $message_text,
            $page_no
        );

        if ($reply_markup !== NULL) {
            // edit the previously sent message,
            // with the buttons
            $bot->api->editMessageText(array(
                "chat_id" => $chat_id,
                "message_id" => $message_id,
                "text" => $GLOBALS["MESG_DETIDE"],
                "parse_mode" => "HTML",
                "disable_web_page_preview" => True,
                "reply_markup" => $reply_markup
            ));
        }

        else {
            // answer back saying search is not found
            // IDEKW how even? :\
            $bot->api->editMessageText(array(
                "chat_id" => $chat_id,
                "message_id" => $message_id,
                "text" => $GLOBALS["GESM_ITEDED"],
                "parse_mode" => "HTML",
                "disable_web_page_preview" => True
            ));
        }
    }

    // how even? :\
    else {
        $bot->api->deleteMessage(array(
            "chat_id" => $chat_id,
            "message_id" => $message_id
        ));
    }
}
