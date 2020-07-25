<?php
/**
 * configurations
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

// setting the bot token from @BotFather
$GLOBALS["TG_BOT_TOKEN"] = getenv("TG_BOT_TOKEN");

// the message that should be displayed,
// when the bot is started
$GLOBALS["START_MESSAGE"] = <<<EOM
Hi.!

I'm Subtitle SearchEr Bot.
I can provide movie / series subtitles.

Type the movie / series name,
and let me try to do the megick..!

Subscribe ℹ️ @SpEcHlDe if you ❤️ using this bot!
EOM;

$GLOBALS["CHECKING_MESSAGE"] = "🤔";

$GLOBALS["ANSWERING_MESSAGE"] = "🧐";

$GLOBALS["SAPI_BASE_URL"] = getenv("SAPI_BASE_URL");

$GLOBALS["MESG_DETIDE"] = <<<EOM
please select your required subtitle
EOM;

$GLOBALS["GESM_ITEDED"] = <<<EOM
sorry. but i could not find subtitle matching the search query.

Please try again using another search..!
EOM;

/**
 * a wraper function to call the search api,
 * and return a reply_markup containing Telegram Buttons
 */
function search_srt_a($s, $p) {
    // set the search URL with the search query
    $search_url = $GLOBALS["SAPI_BASE_URL"] . "/search/" . urlencode($s) . "/" . $p . "";

    // get the responses from the API
    $search_response = json_decode(
        file_get_contents(
            $search_url
        ),
        true
    );

    // initialize an empty array
    // which would store the final "reply_markup"
    $reply_markup_inline_keyboard_arrey = array();

    foreach ($search_response["r"] as $key => $value) {
        // this should contain the CAPTION that can be displayed on the button
        $message_caption = $value["SIQ"];
        // the file size of the SRT file
        $file_size = $value["ISF"];
        // the unique ID of the SRT file, to uniquely identify it
        $sub_id = $value["DMCA_ID"];
        // direct download link of the file,
        // can be empty (at times)
        $direct_download_link = $value["DLL"];

        $reply_markup_inline_keyboard_arrey[] = array(
            array(
                "text" => $message_caption,
                "callback_data" => "" . "dl_" . $sub_id . ""
            )      
        );
    }

    $reply_markup = NULL;

    if (count($reply_markup_inline_keyboard_arrey) > 0) {
        if (count($reply_markup_inline_keyboard_arrey) > 9) {
            if ($p != 1) {
                $reply_markup_inline_keyboard_arrey[] = array(
                    array(
                        "text" => "🔙 Previous",
                        "callback_data" => "page" . "_" . ($p - 1) . ""
                    )      
                );
            }
            $reply_markup_inline_keyboard_arrey[] = array(
                array(
                    "text" => "Next ➡️",
                    "callback_data" => "page" . "_" . ($p + 1) . ""
                )      
            );
        }
        $reply_markup = json_encode(array(
            "inline_keyboard" => $reply_markup_inline_keyboard_arrey
        ));
    }

    return $reply_markup; 
}

/**
 * get subtitle file, from subtitle_id
 */
function get_sub_i($sub_id, $user_id) {
    $sub_get_url = $GLOBALS["SAPI_BASE_URL"] . "/get/" . $sub_id . "/";

    // get the responses from the API
    $subg_response = json_decode(
        file_get_contents(
            $sub_get_url
        ),
        true
    );

    // get the REQuired parameters from the API
    $sub_download_link = $GLOBALS["SAPI_BASE_URL"] . $subg_response["DL_LINK"];
    $sub_language = $subg_response["DL_LANGUAGE"];
    $sub_file_name = $subg_response["DL_SUB_NAME"];
    $sub_file_provider_caption_s = $subg_response["SIQ"];

    // also, return the LEGal DISclaimer,
    // provided by the API, JIC..!
    $sub_legal_disclaimer = $subg_response["LEGAL"];

    $user_directory = __DIR__ . "/../DLS/" . $user_id . "/";
    if (!is_dir($user_directory)) {
        mkdir($user_directory);
    }
    // https://stackoverflow.com/a/6296865/4723940

    $sub_dl_location = $user_directory . $sub_file_name;

    // download the file
    file_put_contents(
        $sub_dl_location,
        file_get_contents(
            $sub_download_link
        )
    );

    $tg_message_caption = "";
    if ($sub_language != "") {
        $tg_message_caption .= "<b>Language</b>: " . $sub_language . "\n";
    }
    if (strpos($sub_file_provider_caption_s, "@") === FALSE) {
        $tg_message_caption .= $sub_file_provider_caption_s;
    }
    // apparently, the LEGAL disclaimer was too LOONG
    // hence, not displaying it
    // $tg_message_caption .= $sub_legal_disclaimer;
    $tg_message_caption .= "\n\nSubtitle provided by @GetSubtitleBot from @SpEcHlDe.";
    
    return array(
        "chat_id" => $user_id,
        "document" => curl_file_create($sub_dl_location),
        "caption" => $tg_message_caption,
        "parse_mode" => "HTML",
        "disable_notification" => True
    );
}

// import Telegram Bot API libraries
require_once __DIR__ . "/../vendor/autoload.php";
