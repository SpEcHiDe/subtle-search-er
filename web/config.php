<?php
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

// import Telegram Bot API libraries
require_once __DIR__ . "/../vendor/autoload.php";
