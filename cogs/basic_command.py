import os
from discord import Client, Embed, Message, Color
from discord.ext import commands
from discord.ext.commands import Cog, Context
if os.path.exists('pro.mode'):
    import secret.secret_pro as secret
    import secret.const_pro as const
else:
    import secret.secret_dev as secret
    import secret.const_dev as const

class BasicCommand(Cog):
    def __init__(self, bot: Client):
        self.bot = bot

    def is_valid(self, message: Message):
        if message.author.bot:
            return False
        if len(message.content) == 0 or message.content[0] == const.COMMAND_PREFIX:
            return False
        return True

    @commands.command(name='he')
    async def command_connect(self, context: Context):
        if self.is_valid(context.message):
            return

        await context.channel.send(embed=self.create_help_embed())
        
    def create_help_embed(self) -> Embed:
        embed = Embed(
            title='ヘルプ・コマンド一覧',
            color=Color.from_rgb(0, 191, 255)
        )
        embed.set_author(name='わくぺのみなさん')
        embed.description = ('**!con**\nVC接続コマンドです。VCに参加した状態で使用してください。\n\n'
                             '**!dc**\nVC切断コマンドです。放置しないでね😢\n\n'
                             '**!he**\nヘルプコマンドです。困ったらこれ。')

        return embed

def setup(bot: Client):
    return bot.add_cog(BasicCommand(bot))
