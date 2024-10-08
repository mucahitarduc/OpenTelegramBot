import os
import opentelegrambot.emoji as emo
import opentelegrambot.constants as con

from telegram import ParseMode
from opentelegrambot.plugin import OpenTelegramPlugin, Category


class Bpmn(OpenTelegramPlugin):

    def get_cmds(self):
        return ["bpmn"]

    @OpenTelegramPlugin.save_data
    @OpenTelegramPlugin.send_typing
    def get_action(self, update, context):
        args = context.args
        if not args:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        cmd = args[0].replace("/", "").lower()

        cmd_found = False
        for plgn in self.tgb.plugins:
            if cmd in plgn.get_cmds():
                cmd_found = True

        if not cmd_found:
            msg = f"{emo.ERROR} Command `/{cmd}` doesn't exist"
            update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
            return

        try:
            bpmn = open(os.path.join(con.BPMN_DIR, f"{cmd}.png"), "rb")
        except Exception:
            msg = f"{emo.INFO} No BPMN diagram found for `/{cmd}`"
            update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
            return

        update.message.reply_photo(
            photo=bpmn,
            caption=f"Process flow for `/{cmd}` command",
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <command>`"

    def get_description(self):
        return "BPMN diagram for a command"

    def get_category(self):
        return Category.BOT
