import os
from discord import ApplicationContext, Client, Embed, Color, slash_command
from discord.ext.commands import Cog
if os.path.exists('pro.mode'):
    import secret.secret_pro as secret
    import secret.const_pro as const
else:
    import secret.secret_dev as secret
    import secret.const_dev as const

class BasicCommand(Cog):
    def __init__(self, bot: Client):
        self.bot = bot

    @slash_command(name='help', description="説明するわよ！")
    async def help(self, context: ApplicationContext):
        await context.respond(embed=self.create_help_embed())
        
    def create_help_embed(self) -> Embed:
        embed = Embed(
            title='ヘルプ・コマンド一覧',
            color=Color.from_rgb(0, 191, 255)
        )
        embed.set_author(name='わくぺのみなさん')
        embed.description = ('**/tts connect**\nVC接続コマンドです。VCに参加した状態で使用してください。\n\n'
                             '**/tts disconnect**\nVC切断コマンドです。放置しないでね😢\n\n'
                             '**/help**\nヘルプコマンドです。困ったらこれ。')

        return embed

def setup(bot: Client):
    return bot.add_cog(BasicCommand(bot))
