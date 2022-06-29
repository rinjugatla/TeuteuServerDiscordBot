import os
from typing import Union
from discord import ApplicationContext, Client, Message, SlashCommandGroup, TextChannel
from discord.ext import tasks
from discord.commands import Option
from discord.ext.commands import Cog
from models.bot.apex_user_rank_model import ApexUserRankModel
from models.database.apex_user_database_model import ApexUserDatabaseModel
from models.database.apex_user_rank_database_model import ApexUserRankDatabaseModel
from utilities.apis.apex_legends_status_api import ApexLegendsStatusAPI
from utilities.database.database_apex_user import DatabaseApexUserUrility
from utilities.database.database_apex_user_rank import DatabaseApexUserRankUrility
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
        self.updating_user_ranks = False
        self.prev_update_user_ranks : list[ApexUserRankDatabaseModel] = None
        self.post_channel : TextChannel = None

    @Cog.listener(name='on_ready')
    async def on_ready(self):
        self.post_channel = self.bot.get_channel(const.APEX_RANK_CHANNEL)
        self.update_user_ranks.start()

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
            users_rank = await self.refresh_apex_users_rank()
        except Exception as ex:
            LogUtility.print_red(str(ex))

        self.updating_user_ranks = False
        if users_rank is None:
            return
        
        changed_users_rank = self.get_changed_user_ranks(users_rank)
        if changed_users_rank is None or len(changed_users_rank) == 0:
            return

        embeds = [user.embed for user in changed_users_rank]

        limit = 10 # embedは10個まで
        if len(embeds) <= limit:
            await self.post_channel.send(embeds=embeds)
            return

        for i in range(0, len(embeds), limit):
            await self.post_channel.send(embeds=embeds[i: i+limit])

    def get_changed_user_ranks(self, users_rank: list[ApexUserRankDatabaseModel]) -> list[ApexUserRankDatabaseModel]:
        """前回と異なるランク情報のみを取得

        Args:
            users_rank (list[ApexUserRankDatabaseModel]): 今回のユーザランク情報

        Returns:
            list[ApexUserRankDatabaseModel]: 更新のあったランク情報
        """
        if self.prev_update_user_ranks is None:
            self.store_prev_users_rank(users_rank)
            return users_rank
        
        changed_users_rank = [user for user in users_rank if not user in self.prev_update_user_ranks]
        self.store_prev_users_rank(users_rank)

        return changed_users_rank

    def store_prev_users_rank(self, users_rank: list[ApexUserRankDatabaseModel]):
        self.prev_update_user_ranks = users_rank

    user_command_group = SlashCommandGroup("apex_user", "ランク情報を追跡するプレイヤの操作")
    rank_command_group = SlashCommandGroup("apex_rank", "ランク情報の操作")
    
    def is_valid(self, message: Message):
        if message.author.bot:
            return False
        if len(message.content) == 0 or message.content[0] == const.COMMAND_PREFIX:
            return False
        return True

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
            user = await self.regist_apex_user(uid, name, platform)
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
        users = self.get_registerd_users()
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
        users = self.get_registerd_users()
        if users is None or len(users) == 0:
            await context.respond(f'ユーザが登録されていません。先に[/apex_user add ~]を実行してください。')
            return

        regsted_uids = [user.uid for user in users]
        is_registerd = (uid in regsted_uids)
        if not is_registerd:
            await context.respond(f'ユーザ({uid})が登録されていません。')
            return
        
        user = [user for user in users if user.uid == uid][0]
        with DatabaseApexUserUrility() as database:
            database.delete_by_uid(user)
        await context.respond(f'{user.name}({uid})のランク情報追跡を取り消しました。')


    @rank_command_group.command(name='show_one', description='ランク情報を表示')
    async def apex_rank_show_one(self, context: ApplicationContext,
                            uid: Option(int, 'uid', required=True),
                            detail: Option(bool, '詳細な情報を表示するか', default=False, required=False)):
        await context.defer()
        user = await self.refresh_apex_user_rank(uid)
        if user is None:
            await context.respond(f'ユーザ情報({uid})の取得に失敗しました。')
            return
        await context.respond(embed=user.embed)

    @rank_command_group.command(name='show_all', description='全員のランク情報を表示')
    async def apex_rank_show_all(self, context: ApplicationContext,
                            detail: Option(bool, '詳細な情報を表示するか', default=False, required=False)):
        await context.defer()
        users_rank = await self.refresh_apex_users_rank()
        embeds = [user.embed for user in users_rank]
        if embeds is None or len(embeds) == 0:
            await context.respond('ユーザが登録されていません。先に[/apex_user add ~]を実行してください。')
            return
        
        self.store_prev_users_rank(users_rank)
        
        limit = 10 # embedは10個まで
        if len(embeds) <= limit:
            await context.respond(embeds=embeds)
            return
        
        for i in range(0, len(embeds), limit):
            await context.respond(embeds=embeds[i: i+limit])

    # @rank_command_group.command(name='refresh', description='ランク情報を強制的に更新する')
    # async def apex_rank_refresh(self, context: ApplicationContext):
    #     pass

    async def regist_apex_user(self, uid: int, name: str, platform: str) -> Union[ApexUserRankModel, None]:
        """ユーザ情報をDBに登録

        Args:
            uid (int): uidまたはnameの指定が必須
            name (str): uidまたはnameの指定が必須
            platform (str): プラットフォーム(PC, PS4, X1, SWITCH)

        Returns:
            Union[ApexUserRankModel, None]: ランク情報を含むユーザ情報
        """
        if uid is None and name is None:
            return None
        
        user = None
        try:
            if not uid is None:
                user = await ApexLegendsStatusAPI.get_user_by_uid(uid, platform)
            elif not name is None:
                user = await ApexLegendsStatusAPI.get_user_by_name(name, platform)
        except:
            raise

        if user is None:
            return None
        with DatabaseApexUserUrility() as database:
            database.update_by_uid(user)
            return user

    def get_registerd_users(self) -> list[ApexUserDatabaseModel]:
        """データベースに登録済みのユーザ情報を取得
        """
        with DatabaseApexUserUrility() as database:
            users_list = database.select_users()
            users = [ApexUserDatabaseModel(user) for user in users_list]
            return users

    async def refresh_apex_user_rank(self, uid: int) -> Union[ApexUserRankModel, None]:
        """データベースに登録済みの追跡対象ユーザのランク情報を取得して登録
        """
        user = None
        with DatabaseApexUserUrility() as database:
            user: ApexUserDatabaseModel = database.select_by_uid(uid=uid)

        rank_histories = None
        refreshed_user = await ApexLegendsStatusAPI.get_user_by_uid(user.uid, user.platform)
        with DatabaseApexUserRankUrility() as database:
            database.insert_rank_by_uid(refreshed_user)
            rank_histories = database.select_by_user_uid(user.uid, 2)

        if rank_histories is None:
            return refreshed_user
        ranks = self.calc_user_rank_changes(rank_histories)
        if ranks is None:
            return None
        return ranks[-1]
    
    async def refresh_apex_users_rank(self) -> Union[list[ApexUserRankModel], list[ApexUserRankDatabaseModel], None]:
        """データベースに登録されている追跡対象のユーザすべてのランク情報を取得して登録
        """
        users = self.get_registerd_users()
        if users is None or len(users) == 0:
            return None

        rank_histories = None
        refreshed_users = [await ApexLegendsStatusAPI.get_user_by_uid(uid=user.uid, platform=user.platform) for user in users]
        with DatabaseApexUserRankUrility() as database:
            database.insert_ranks_by_uid(refreshed_users)
            uids = [user.uid for user in users]
            rank_histories = database.select_by_users_uid(uids, 2)

        if rank_histories is None:
            return refreshed_users
        
        # 最新のランク情報のみ抽出
        users_ranks = self.calc_users_ranks_changes(rank_histories)
        users_rank = [users_rank[-1] for users_rank in users_ranks]
        return users_rank

    def calc_user_rank_changes(self, ranks: list[dict]) -> Union[list[ApexUserRankDatabaseModel], None]:
        """差分を含むランク情報を計算

        Args:
            ranks (list[dict]): ランク情報

        Returns:
            Union[list[ApexUserRankDatabaseModel], None]: 差分を含むランク情報
        """
        length = len(ranks)
        if length == 0:
            LogUtility.print_red('ユーザランク情報の取得に失敗しました。')
            return None
        elif length == 1:
            return [ApexUserRankDatabaseModel(ranks[0])]
        
        histories: list[ApexUserRankDatabaseModel] = []
        for rank in ranks:
            histories.append(ApexUserRankDatabaseModel(rank))
        for i in range(len(histories) - 1):
            histories[i + 1].set_change(histories[i])
        return histories

    def calc_users_ranks_changes(self, users_ranks: list[list[dict]]) -> Union[list[list[ApexUserDatabaseModel]], None]:
        """差分を含むランク情報を計算

        Args:
            users_ranks (list[list[dict]]): 複数のユーザのランク情報

        Returns:
            Union[list[list[ApexUserDatabaseModel]], None]: 差分を含むランク情報
        """
        users_histories = []
        for user_ranks in users_ranks:
            user_histories = self.calc_user_rank_changes(user_ranks)
            if user_histories is not None:
                users_histories.append(user_histories)
        return users_histories

def setup(bot: Client):
    return bot.add_cog(ApexStats(bot))
