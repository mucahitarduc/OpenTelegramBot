import opentelegrambot.emoji as emo
import opentelegrambot.utils as utl

from telegram import ParseMode
from opentelegrambot.ratelimit import RateLimit
from opentelegrambot.api.apicache import APICache
from opentelegrambot.api.coinpaprika import CoinPaprika
from opentelegrambot.plugin import OpenTelegramPlugin, Category


class Team(OpenTelegramPlugin):

    def get_cmds(self):
        return ["t", "team"]

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

        if len(args) > 1:
            update.message.reply_text(
                text=f"{emo.ERROR} Only one argument allowed",
                parse_mode=ParseMode.MARKDOWN)
            return

        if RateLimit.limit_reached(update):
            return

        coin = args[0].upper()
        msg = str()

        try:
            response = APICache.get_cp_coin_list()
        except Exception as e:
            return self.handle_error(e, update)

        for c in response:
            if c["symbol"] == coin:
                try:
                    cp_coin_detail = CoinPaprika().get_coin_by_id(c["id"])["team"]
                except Exception as e:
                    return self.handle_error(e, update)

                for p in cp_coin_detail:
                    details = utl.esc_md(f"/_people__{p['id'].replace('-', '_')}")
                    msg += f"`{p['name']}\n{p['position']}`\n{details}\n\n"
                break

        if not msg:
            update.message.reply_text(
                text=f"{emo.INFO} No team data for *{coin}*",
                parse_mode=ParseMode.MARKDOWN)
            return

        msg = f"`Team behind {coin}`\n\n{msg}"

        for message in utl.split_msg(msg):
            update.message.reply_text(
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <symbol>`"

    def get_description(self):
        return "Info about team behind a coin"

    def get_category(self):
        return Category.GENERAL
