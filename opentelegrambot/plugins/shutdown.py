import threading
import opentelegrambot.emoji as emo

from opentelegrambot.plugin import OpenTelegramPlugin


class Shutdown(OpenTelegramPlugin):

    def get_cmds(self):
        return ["shutdown"]

    @OpenTelegramPlugin.only_owner
    @OpenTelegramPlugin.send_typing
    def get_action(self, update, context):
        args = context.args
        bot = update.message.bot
        msg = f"{emo.GOODBYE} Shutting down..."
        update.message.reply_text(msg)

        threading.Thread(target=self._shutdown_thread).start()

    def get_usage(self):
        return None

    def get_description(self):
        return None

    def get_category(self):
        return None

    def _shutdown_thread(self):
        self.tgb.updater.stop()
        self.tgb.updater.is_idle = False
