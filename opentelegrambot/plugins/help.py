from telegram import ParseMode
from opentelegrambot.plugin import OpenTelegramPlugin, Category


class Help(OpenTelegramPlugin):

    def get_cmds(self):
        return ["h", "help"]

    @OpenTelegramPlugin.save_data
    @OpenTelegramPlugin.send_typing
    def get_action(self, update, context):
        args = context.args
        bot = update.message.bot
        cat_dict = dict()
        for p in self.tgb.plugins:
            if p.get_category() and p.get_description():
                des = f"/{p.get_cmds()[0]} - {p.get_description()}\n"

                if p.get_category() not in cat_dict:
                    cat_dict[p.get_category()] = [des]
                else:
                    lst = cat_dict[p.get_category()]
                    lst.append(des)

        msg = str()
        for c in Category.get_categories():
            v = next(iter(c.values()))

            if v in cat_dict:
                msg += f"*{v}*\n"

                for cmd in sorted(cat_dict[v]):
                    msg += f"{cmd}"

                msg += "\n"

        msg += "Visit the [homepage](https://endogen.github.io/OpenCryptoBot) " \
               "to get an explanation for every command an every possible argument"

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)

    def get_usage(self):
        return None

    def get_description(self):
        return None

    def get_category(self):
        return None
