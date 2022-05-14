import os
from discord.ext.commands import Bot
if os.path.exists('pro.mode'):
    import secret.secret_pro as secret
    import secret.const_pro as const
else:
    import secret.secret_dev as secret
    import secret.const_dev as const

class DiscordBot():
    def __init__(self, is_debug: bool = False):
        
        self.bot = Bot(command_prefix = const.COMMAND_PREFIX, 
            # intents = self.create_intents(),
            enable_debug_events = is_debug)
        
    # def create_intents(self) -> Intents:
    #     intents = Intents.all()
    #     intents.typing = False
    #     intents.presences = False
    #     return intents

    def start(self):
        for name in const.HOOL_MODULES_FIXED:
            self.bot.load_extension(name)
        self.bot.run(secret.TOKEN)

bot = DiscordBot()
bot.start()