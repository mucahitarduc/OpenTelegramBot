from telegram import ParseMode
import opentelegrambot.emoji as emo
from opentelegrambot.config import ConfigManager as Cfg
from opentelegrambot.plugin import OpenTelegramPlugin, Category


class Feedback(OpenTelegramPlugin):

    def get_cmds(self):
        return ["feedback"]

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

        user = update.message.from_user
        if user.username:
            name = f"@{user.username}"
        else:
            name = user.first_name

        feedback = update.message.text.replace(f"/{self.get_cmds()[0]} ", "")

        for admin in Cfg.get("admin_id"):
            bot.send_message(admin, f"Feedback from {name}: {feedback}")

        update.message.reply_text(f"Thanks for letting us know {emo.TOP}")

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <your feedback>`\n"

    def get_description(self):
        return "Send us your feedback"

    def get_category(self):
        return Category.BOT
