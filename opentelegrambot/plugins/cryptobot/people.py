import opentelegrambot.emoji as emo
import opentelegrambot.utils as utl

from telegram import ParseMode
from opentelegrambot.ratelimit import RateLimit
from opentelegrambot.api.coinpaprika import CoinPaprika
from opentelegrambot.plugin import OpenTelegramPlugin, Category


class People(OpenTelegramPlugin):

    def get_cmds(self):
        return ["pe", "people"]

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

        if len(args) > 1:
            name = "-".join(args).lower()
        else:
            name = args[0]

        name_clean = name.replace('-', " ").title()
        msg = str()

        try:
            d = CoinPaprika().get_people_by_id(name)
        except Exception as e:
            return self.handle_error(e, update)

        if "description" in d and d["description"]:
            msg = f"`{d['description']}`\n\n"

        if "links" in d and d["links"]:
            for k, v in d["links"].items():
                url = v[0]["url"]
                fol = v[0]["followers"] if "followers" in v[0] else None

                fol_str = f"({utl.format(fol)} Followers)" if fol else ""
                msg += f"`{k.title()} {fol_str}`\n{utl.esc_md(url)}\n"

        if "positions" in d and d["positions"]:
            msg += "\n`Positions:`\n" if msg else "`Positions:`\n"

            for pos in d["positions"]:
                msg += f"`{pos['coin_symbol']} - {pos['position']}`\n"

        if not msg:
            update.message.reply_text(
                text=f"{emo.INFO} No person with name *'{name_clean}'* found",
                parse_mode=ParseMode.MARKDOWN)
            return

        msg = f"`{name_clean}`\n\n{msg}"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <forename>-<surname>`"

    def get_description(self):
        return "Info about person from a team"

    def get_category(self):
        return Category.GENERAL
