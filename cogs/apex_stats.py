import os, traceback, aiohttp
from typing import Union
from discord import ApplicationContext, Client, Message, SlashCommandGroup, TextChannel
from discord.ext import tasks
from discord.commands import Option
from discord.ext.commands import Cog
from utilities.apex_user_rank_utility import ApexUserRankUtility
from utilities.database.database_apex_user import DatabaseApexUserUrility
from utilities.log import LogUtility
if os.path.exists('pro.mode'):
    import secret.secret_pro as secret
    import secret.const_pro as const
else:
    import secret.secret_dev as secret
    import secret.const_dev as const

class ApexStats(Cog):
    def __init__(self, bot: Client):
        self.bot = bot
        self.is_on_ready_done = False
        self.updating_user_ranks = False
        self.is_first_update_user_rank_done = False
        self.rank_utility = ApexUserRankUtility()
        self.post_channel : TextChannel = None

    @Cog.listener(name='on_ready')
    async def on_ready(self):
        if not self.is_on_ready_done:
            self.post_channel = self.bot.get_channel(const.APEX_RANK_CHANNEL)
            self.update_user_ranks.start()
            self.is_on_ready_done = True

    @tasks.loop(minutes=2)
    async def update_user_ranks(self):
        """一定時間毎にランク情報を取得、更新のあったユーザのランク情報のみ表示
        """
        # 多重実行回避
        if self.updating_user_ranks:
            return

        LogUtility.print_green('ランク情報の定期取得を開始します。')
        self.updating_user_ranks = True

        users_rank = None
        try:
            users_rank = await self.rank_utility.refresh_apex_users_rank()
        except Exception as ex:
            LogUtility.print_error(str(ex), 'update_user_ranks', traceback.format_exc())

        self.updating_user_ranks = False
        if users_rank is None:
            return
        
        changed_users_rank = self.rank_utility.get_changed_user_ranks(users_rank)
        if changed_users_rank is None or len(changed_users_rank) == 0:
            return

        # 初回実行時は出力しない
        if not self.is_first_update_user_rank_done:
            self.is_first_update_user_rank_done = True
            return

        embeds = [user.embed for user in changed_users_rank]
        limit = 10 # embedは10個まで
        if len(embeds) <= limit:
            await self.post_channel.send(embeds=embeds)
            return

        for i in range(0, len(embeds), limit):
            await self.post_channel.send(embeds=embeds[i: i+limit])

    user_command_group = SlashCommandGroup("apex_user", "ランク情報を追跡するプレイヤの操作")
    rank_command_group = SlashCommandGroup("apex_rank", "ランク情報の操作")

    @user_command_group.command(name='add', description='ランク情報追跡ユーザを追加')
    async def apex_user_add(self, context: ApplicationContext,
                            platform: Option(str, 'プラットフォーム名', choices=['PC', 'PS4', 'X1', 'SWITCH'], default='PC', required=True),
                            uid: Option(int, 'UID', required=False),
                            name: Option(str, 'アカウント名', required=False)):
        await context.defer()
        if uid is None and name is None:
            await context.respond('uidまたはnameを指定してください。')
            return
        try:
            user = await self.rank_utility.regist_apex_user(uid, name, platform)
        except Exception as ex: 
            await context.respond(str(ex))
            return

        if user is None:
            await context.respond('ユーザの追加に失敗しました。')
        else:
            await context.respond(f'{user.name}({user.uid})のランク情報の追跡を開始します。')

    @user_command_group.command(name='show', description='ランク情報追跡ユーザ一覧を表示')
    async def apex_user_show(self, context: ApplicationContext):
        await context.defer()
        users = self.rank_utility.get_registerd_users()
        if users is None or len(users) == 0:
            await context.respond(f'ユーザが登録されていません。先に[/apex_user add ~]を実行してください。')
            return

        users_summary_list = [user.summary() for user in users]
        users_preview = '\n'.join(users_summary_list)
        await context.respond(f'登録済みのユーザ\n{users_preview}')

    @user_command_group.command(name='remove', description='ランク情報の追跡を取り消し')
    async def apex_user_remove(self, context: ApplicationContext,
                                uid: Option(int, 'UID', required=True)):
        await context.defer()
        
        user = None
        try:
            user = await self.rank_utility.get_apex_user(uid)
        except Exception as ex:
            await context.respond(str(ex))
            return

        with DatabaseApexUserUrility() as database:
            database.delete_by_uid(user)
        await context.respond(f'{user.name}({uid})のランク情報追跡を取り消しました。')

    @user_command_group.command(name='set_icon', description='アイコンを設定')
    async def apex_user_set_icon(self, context: ApplicationContext,
                                 uid: Option(int, 'UID', required=True),
                                 url: Option(str, 'アイコンURL', required=True)):
        await context.defer()

        is_valid_url = await self.is_valid_image_url(url)
        if not is_valid_url:
            await context.respond(f'画像URLが不正です。JPEGまたはPNGの画像を指定してください。')
            return

        user = None
        try:
            user = await self.rank_utility.get_apex_user(uid)
        except Exception as ex:
            await context.respond(str(ex))
            return

        with DatabaseApexUserUrility() as database:
            database.update_icon_url_by_uid(user, url)
            
        await context.respond(f'ユーザ({uid})のアイコンを設定しました。')

    async def is_valid_image_url(self, url: str) -> bool:
        """有効な画像URLか確認
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as res:
                    content_type = res.headers['content-type']
                    is_valid = content_type.startswith('image/')
                    LogUtility.print_green(f'is_valid_image_url {url} {content_type} {is_valid}')
                    return is_valid
        except Exception as ex:
            LogUtility.print_error(str(ex), '画像のURL解析', traceback.format_exception())
            return False

    @rank_command_group.command(name='show_one', description='ランク情報を表示')
    async def apex_rank_show_one(self, context: ApplicationContext,
                            uid: Option(int, 'uid', required=True),
                            detail: Option(bool, '詳細な情報を表示するか', default=False, required=False)):
        await context.defer()
        
        try:
            await self.rank_utility.get_apex_user(uid)
        except Exception as ex:
            await context.respond(str(ex))
            return

        user = await self.rank_utility.refresh_apex_user_rank(uid)
        if user is None:
            await context.respond(f'ユーザ情報({uid})の取得に失敗しました。')
            return
        await context.respond(embed=user.embed)

    @rank_command_group.command(name='show_all', description='全員のランク情報を表示')
    async def apex_rank_show_all(self, context: ApplicationContext,
                            detail: Option(bool, '詳細な情報を表示するか', default=False, required=False)):
        await context.defer()
        users_rank = await self.rank_utility.refresh_apex_users_rank()
        embeds = [user.embed for user in users_rank]
        if embeds is None or len(embeds) == 0:
            await context.respond('ユーザが登録されていません。先に[/apex_user add ~]を実行してください。')
            return
        
        self.rank_utility.store_prev_users_rank(users_rank)
        
        limit = 10 # embedは10個まで
        if len(embeds) <= limit:
            await context.respond(embeds=embeds)
            return
        
        for i in range(0, len(embeds), limit):
            await context.respond(embeds=embeds[i: i+limit])

    # @rank_command_group.command(name='refresh', description='ランク情報を強制的に更新する')
    # async def apex_rank_refresh(self, context: ApplicationContext):
    #     pass

def setup(bot: Client):
    return bot.add_cog(ApexStats(bot))
