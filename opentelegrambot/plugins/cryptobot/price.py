import decimal
import opentelegrambot.emoji as emo
import opentelegrambot.utils as utl

from telegram import ParseMode
from opentelegrambot.ratelimit import RateLimit
from opentelegrambot.api.apicache import APICache
from opentelegrambot.api.coingecko import CoinGecko
from opentelegrambot.plugin import OpenTelegramPlugin, Category, Keyword


class Price(OpenTelegramPlugin):

    CG_URL = "https://www.coingecko.com/en/coins/"

    def get_cmds(self):
        return ["p", "price"]

    @OpenTelegramPlugin.save_data
    @OpenTelegramPlugin.send_typing
    def get_action(self, update, context):
        args = context.args
        bot = update.message.bot
        # TODO: Do this in every plugin
        keywords = utl.get_kw(args)
        arg_list = utl.del_kw(args)

        # TODO: Do this in most other plugins
        if not arg_list:
            if not keywords.get(Keyword.INLINE):
                update.message.reply_text(
                    text=f"Usage:\n{self.get_usage()}",
                    parse_mode=ParseMode.MARKDOWN)
            return

        vs_cur = str()

        if "-" in arg_list[0]:
            pair = arg_list[0].split("-", 1)
            vs_cur = pair[1].upper()
            coin = pair[0].upper()
        else:
            coin = arg_list[0].upper()

        exchange = str()
        if len(arg_list) > 1:
            exchange = arg_list[1]

        try:
            response = APICache.get_cg_coins_list()
        except Exception as e:
            return self.handle_error(e, update)

        coin_id = str()
        coin_name = str()
        for entry in response:
            if entry["symbol"].upper() == coin:
                coin_id = entry["id"]
                coin_name = entry["name"]
                break

        if RateLimit.limit_reached(update):
            return

        cg = CoinGecko()
        msg = str()

        if exchange:
            try:
                result = cg.get_coin_by_id(coin_id)
            except Exception as e:
                return self.handle_error(e, update)

            if result:
                vs_list = list()

                if vs_cur:
                    vs_list = vs_cur.split(",")

                for ticker_len in result["tickers"]:
                    if ticker_len["market"]["name"].upper() == exchange.upper():
                        if ticker_len["base"] != coin:
                            base_coin = ticker_len["base"]
                        else:
                            base_coin = ticker_len["target"]

                        if vs_list:
                            if base_coin in vs_list:
                                price = utl.format(ticker_len["last"], force_length=True)
                                msg += f"`{base_coin}: {price}`\n"
                        else:
                            price = utl.format(ticker_len["last"], force_length=True)
                            msg += f"`{base_coin}: {price}`\n"
        else:
            if not vs_cur:
                if coin == "BTC":
                    vs_cur = "ETH,USD,EUR"
                elif coin == "ETH":
                    vs_cur = "BTC,USD,EUR"
                else:
                    vs_cur = "BTC,ETH,USD,EUR"

            try:
                result = cg.get_simple_price(coin_id, vs_cur)
            except Exception as e:
                return self.handle_error(e, update)

            if result:
                for symbol, price in next(iter(result.values())).items():
                    if symbol in utl.get_fiat_list():
                        if decimal.Decimal(str(price)).as_tuple().exponent > -3:
                            price = utl.format(price, decimals=2, force_length=True)
                        else:
                            price = utl.format(price, force_length=True)
                    else:
                        price = utl.format(price, force_length=True)

                    msg += f"`{symbol.upper()}: {price}`\n"

        if msg:
            if exchange:
                ticker_len = 0
                for line in msg.split("\n"):
                    length = len(line[:line.find(":")])
                    if ticker_len < length:
                        ticker_len = length

                message = str()
                for line in msg.split("\n"):
                    if line:
                        lst = line.split(" ")
                        index = ticker_len + 2 + len(lst[1]) - len(lst[0])
                        price = "{1:>{0}}".format(index, lst[1])
                        message += f"{lst[0]}{price}\n"

                msg = f"`{coin} ({coin_name}) on {exchange.capitalize()}`\n\n" + message
            else:
                msg = f"`{coin} ({coin_name})`\n\n" + msg

            # Add link to source of data (CoinGecko)
            msg += f"\n[Details on CoinGecko]({self.CG_URL}{coin_id})"
        else:
            msg = f"{emo.ERROR} Can't retrieve data for *{coin}*"

        if keywords.get(Keyword.INLINE):
            return msg

        self.send_msg(msg, update, keywords)

    def get_usage(self):
        bot_name = self.tgb.updater.bot.name

        return f"`" \
               f"/{self.get_cmds()[0]} <symbol>\n\n" \
               f"/{self.get_cmds()[0]} <symbol> <exchange>\n\n" \
               f"/{self.get_cmds()[0]} <symbol>-<target symbol>,[...]\n\n" \
               f"{bot_name} /{self.get_cmds()[0]} <symbol>.\n\n" \
               f"{bot_name} /{self.get_cmds()[0]} <symbol>-<target symbol>,[...]." \
               f"`"

    def get_description(self):
        return "Coin price"

    def get_category(self):
        return Category.PRICE

    def inline_mode(self):
        return True
