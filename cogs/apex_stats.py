import os, aiohttp, json
from typing import Union
from discord import ApplicationContext, Client, Message, SlashCommandGroup
from discord.commands import Option
from discord.ext.commands import Cog, slash_command
from models.bot.apex_user_rank_model import ApexUserRankModel
from models.database.apex_user_database_model import ApexUserDatabaseModel

from secret.secret_dev import APEX_TOKEN
from utilities.database.database_apex_user import DatabaseApexUserUrility
if os.path.exists('pro.mode'):
    import secret.secret_pro as secret
    import secret.const_pro as const
else:
    import secret.secret_dev as secret
    import secret.const_dev as const

class ApexStats(Cog):
    def __init__(self, bot: Client):
        self.bot = bot

    user_command_group = SlashCommandGroup("apex_user", "ランクポイント統計を追跡するプレイヤの操作")
    rank_command_group = SlashCommandGroup("apex_rank", "ランクポイントの統計の操作")
    
    def is_valid(self, message: Message):
        if message.author.bot:
            return False
        if len(message.content) == 0 or message.content[0] == const.COMMAND_PREFIX:
            return False
        return True

    @user_command_group.command(name='add', description='ランク統計追跡ユーザを追加')
    async def apex_user_add(self, context: ApplicationContext,
                            platform: Option(str, 'プラットフォーム名', choices=['PC', 'PS4', 'X1', 'SWITCH'], default='PC', required=True),
                            uid: Option(int, 'UID', required=False),
                            name: Option(str, 'アカウント名', required=False)):
        if uid is None and name is None:
            await context.respond('uidまたはnameを指定してください。')
            return
            
        user = await self.add_apex_user(uid, name, platform)
        if user is None:
            await context.respond('ユーザの追加に失敗しました。')
        else:
            user: ApexUserRankModel
            await context.respond(f'ユーザ{user.name}({user.uid})を追加しました。')

    @user_command_group.command(name='show', description='ランク統計追跡ユーザを表示')
    async def apex_user_show(self, context: ApplicationContext):
        users = self.get_users()
        if users is None or len(users) == 0:
            await context.respond(f'ユーザが登録されていません。先に[/apex_user add ~]を実行してください。')
            return

        users_summary_list = [user.summary() for user in users]
        users_preview = '\n'.join(users_summary_list)
        await context.respond(f'登録済みのユーザ\n{users_preview}')

    # 未実装
    # @user_command_group.command(name='remove', description='ランク統計の追跡を取り消し')
    # async def apex_user_remove(self, context: ApplicationContext,
    #                             uid: Option(int, 'UID', required=True)):
    #     pass
    
    @rank_command_group.command(name='show_one', description='ランク統計を表示')
    async def apex_rank_show_one(self, context: ApplicationContext,
                            uid: Option(int, 'uid', required=True),
                            detail: Option(bool, '詳細な情報を表示するか', default=False, required=False)):
        pass

    @rank_command_group.command(name='show_all', description='全員のランク統計を表示')
    async def apex_rank_show_one(self, context: ApplicationContext,
                            detail: Option(bool, '詳細な情報を表示するか', default=False, required=False)):
        pass

    @rank_command_group.command(name='refresh', description='ランク情報を強制的に更新する')
    async def apex_rank_refresh(self, context: ApplicationContext):
        pass


    async def add_apex_user(self, uid: int, name: str, platform: str) -> Union[ApexUserRankModel, None]:
        if uid is None and name is None:
            return None
        
        user = None
        if not uid is None:
            user = await self.get_user_by_uid(uid, platform)
        elif not name is None:
            user = await self.get_user_by_name(name, platform)

        if user is None:
            return None

        with DatabaseApexUserUrility() as database:
            database.update_by_uid(user)
            return user

    def get_users(self) -> list[ApexUserDatabaseModel]:
        with DatabaseApexUserUrility() as database:
            users_list = database.select_users()
            users = [ApexUserDatabaseModel(user) for user in users_list]
            return users

    async def get_user_by_uid(self, uid: int, platform: str) -> ApexUserRankModel:
        base_url = 'https://api.mozambiquehe.re/bridge?uid=:uid:&platform=:platform:&merge=true&removeMerged=true'
        url = base_url.replace(':uid:', str(uid)).replace(':platform:', platform)
        user = await self.post_user_api(url)
        return user

    async def get_user_by_name(self, name: str, platform: str) -> ApexUserRankModel:
        base_url = 'https://api.mozambiquehe.re/bridge?player=:name:&platform=:platform:&merge=true&removeMerged=true'
        url = base_url.replace(':name:', name).replace(':platform:', platform)
        user = await self.post_user_api(url)
        return user

    async def post_user_api(self, url: str) -> ApexUserRankModel:
        """ApexLegendsUserStatus
            https://apexlegendsapi.com/#query-by-name
            https://apexlegendsapi.com/#query-by-uid

        Args:
            url (str): エンドポイント

        Returns:
            ApexUserRankModel: ランク情報を含むユーザ情報
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=self.get_api_header()) as response:
                if response.status != 200:
                    return None

                # header: Content-Type: text/plain;charset=UTF-8なのでresponse.json()は利用不可
                data = json.loads(await response.text())
                user = ApexUserRankModel(data)
                return user

    def get_api_header(self) -> dict:
        return {
            'Content-Type': 'application/json;',
            'Authorization': secret.APEX_TOKEN
        }

def setup(bot: Client):
    return bot.add_cog(ApexStats(bot))
