import opentelegrambot.emoji as emo

from telegram import ParseMode
from opentelegrambot.ratelimit import RateLimit
from opentelegrambot.api.apicache import APICache
from opentelegrambot.plugin import OpenTelegramPlugin, Category


class Search(OpenTelegramPlugin):

    def get_cmds(self):
        return ["se", "search"]

    @OpenTelegramPlugin.save_data
    @OpenTelegramPlugin.send_typing
    def get_action(self, update, context):
        args = context.args
        bot = update.message.bot
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        if RateLimit.limit_reached(update):
            return

        search = args[0]
        msg = str()

        try:
            response = APICache.get_cg_coins_list()
        except Exception as e:
            return self.handle_error(e, update)

        for entry in response:
            if search.lower() in entry["name"].lower():
                name = entry["name"]
                symbol = entry["symbol"]

                msg += f"`{name} - {symbol.upper()}`\n"

        if msg:
            msg = f"`Coin-search for '{search}'`\n\n" + msg
        else:
            msg = f"{emo.INFO} No coin with '*{search}*' found"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <coin name>`"

    def get_description(self):
        return "Search for symbol by coin name"

    def get_category(self):
        return Category.GENERAL
