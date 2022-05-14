import os
from discord import Client
from discord.ext.commands import Cog
from utilities.log import LogUtility
if os.path.exists('pro.mode'):
    import secret.secret_pro as secret
    import secret.const_pro as const
else:
    import secret.secret_dev as secret
    import secret.const_dev as const

class BasicEvent(Cog):
    def __init__(self, bot: Client):
        self.bot = bot
        self.is_on_ready = False
        self.is_regist_report_view = False

    @Cog.listener(name='on_ready')
    async def on_ready(self):
        if not self.is_on_ready:
            LogUtility.print_login(self.bot)
            self.is_on_ready = True

def setup(bot: Client):
    return bot.add_cog(BasicEvent(bot))