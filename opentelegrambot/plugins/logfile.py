import os
import opentelegrambot.emoji as emo
import opentelegrambot.constants as con

from opentelegrambot.plugin import OpenCryptoPlugin, Category


class Logfile(OpenCryptoPlugin):

    def get_cmds(self):
        return ["log"]

    @OpenCryptoPlugin.only_owner
    @OpenCryptoPlugin.send_typing
    def get_action(self, update, context):
        args = context.args
        bot = update.message.bot
        base_dir = os.path.abspath('./')

        update.message.reply_document(
            caption=f"{emo.CHECK} Current Logfile",
            document=open(os.path.join(base_dir, con.LOG_DIR, con.LOG_FILE), 'rb'))

    def get_usage(self):
        return f"`/{self.get_cmds()[0]}`"

    def get_description(self):
        return "Returns current logfile"

    def get_category(self):
        return Category.BOT
