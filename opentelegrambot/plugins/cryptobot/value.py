import opentelegrambot.emoji as emo
import opentelegrambot.utils as utl

from telegram import ParseMode
from opentelegrambot.ratelimit import RateLimit
from opentelegrambot.api.apicache import APICache
from opentelegrambot.api.coingecko import CoinGecko
from opentelegrambot.plugin import OpenTelegramPlugin, Category


class Value(OpenTelegramPlugin):

    def get_cmds(self):
        return ["v", "value"]

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

        vs_cur = "btc,eth,usd,eur"

        if "-" in args[0]:
            pair = args[0].split("-", 1)
            vs_cur = pair[1].lower()
            coin = pair[0].upper()
        else:
            coin = args[0].upper()

        if len(args) > 1 and utl.is_number(args[1]):
            qty = args[1]
        else:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        if RateLimit.limit_reached(update):
            return

        prices = dict()

        try:
            response = APICache.get_cg_coins_list()
        except Exception as e:
            return self.handle_error(e, update)

        # Get coin ID
        for entry in response:
            if entry["symbol"].upper() == coin:
                try:
                    data = CoinGecko().get_coin_by_id(entry["id"])
                except Exception as e:
                    return self.handle_error(e, update)

                prices = data["market_data"]["current_price"]
                break

        try:
            qty_float = float(qty)
        except Exception:
            update.message.reply_text(
                text=f"{emo.ERROR} Quantity '{qty}' not valid",
                parse_mode=ParseMode.MARKDOWN)
            return

        msg = str()

        for c in vs_cur.split(","):
            if c in prices:
                value = utl.format(prices[c] * qty_float)
                msg += f"`{c.upper()}: {value}`\n"

        if msg:
            msg = f"`Value of {qty} {coin}`\n\n" + msg
        else:
            msg = f"{emo.ERROR} Can't retrieve data for *{coin}*"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <symbol>(-<target symbol>,[...]) <quantity>`"

    def get_description(self):
        return "Value of coin quantity"

    def get_category(self):
        return Category.PRICE
