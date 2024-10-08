import opentelegrambot.emoji as emo

from telegram import ParseMode
from opentelegrambot.plugin import OpenTelegramPlugin, Category


class Manual(OpenTelegramPlugin):

    def get_cmds(self):
        return ["man", "manual"]

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

        msg = None
        cmd = args[0].lower()
        cmd = cmd[1:] if cmd.startswith("/") else cmd

        for p in self.tgb.plugins:
            if cmd.lower() in p.get_cmds():
                msg = p.get_usage() if p.get_usage() else None

        if not msg:
            update.message.reply_text(
                text=f"{emo.INFO} No details for command `{cmd}` available",
                parse_mode=ParseMode.MARKDOWN)
            return

        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <command>`"

    def get_description(self):
        return "Show how to use a command"

    def get_category(self):
        return Category.BOT
