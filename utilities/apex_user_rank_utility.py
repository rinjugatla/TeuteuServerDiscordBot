import os
from typing import Union
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

class ApexUserRankUtility():
    def __init__(self):
        self.__prev_update_user_ranks : list[ApexUserRankDatabaseModel] = None

    async def get_apex_user(self, uid: int) -> ApexUserDatabaseModel:
        """UIDからユーザ情報を取得

        Args:
            uid (int): ApexユーザUID

        Raises:
            Exception: 指定のユーザが見つからない

        Returns:
            list[ApexUserDatabaseModel]: ユーザ情報
        """
        users = self.get_registerd_users()
        if users is None or len(users) == 0:
            raise Exception('ユーザが登録されていません。先に[/apex_user add ~]を実行してください。')

        regsted_uids = [user.uid for user in users]
        is_registerd = (uid in regsted_uids)
        if not is_registerd:
            raise Exception(f'ユーザ({uid})が登録されていません。')
        
        user = [user for user in users if user.uid == uid][0]
        return user

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

    async def update_apex_user(self, user: dict):
        """ユーザ情報を更新

        Args:
            user (dict): 古いユーザ情報
        """
        if user is None or 'uid' not in user or 'platform' not in user:
            return
        latest_user = await ApexLegendsStatusAPI.get_user_by_uid(user['uid'], user['platform'])
        with DatabaseApexUserUrility() as database:
            database.update_by_uid(latest_user)

    async def update_apex_users(self, users: list[dict]):
        """複数のユーザの情報を更新

        Args:
            users (list[dict]): 古いユーザ情報
        """
        if users is None or len(users) == 0:
            return

        latest_users = []
        for user in users:
            if user is None or 'uid' not in user or 'platform' not in user:
                continue

            latest_user = await ApexLegendsStatusAPI.get_user_by_uid(user['uid'], user['platform'])
            if latest_user is None:
                continue
            latest_users.append(latest_user)
        
        with DatabaseApexUserUrility() as database:
            for latest_user in latest_users:
                database.update_by_uid(latest_user)

    def get_registerd_users(self) -> list[ApexUserDatabaseModel]:
        """データベースに登録済みのユーザ情報を取得
        """
        with DatabaseApexUserUrility() as database:
            users_list = database.select_users()
            users = [ApexUserDatabaseModel(user) for user in users_list]
            return users

    def store_prev_users_rank(self, users_rank: list[ApexUserRankDatabaseModel]):
        """前回のランク情報を保存

        Args:
            users_rank (list[ApexUserRankDatabaseModel]): 前回のユーザランク情報
        """
        self.__prev_update_user_ranks = users_rank

    def get_changed_user_ranks(self, users_rank: list[ApexUserRankDatabaseModel]) -> list[ApexUserRankDatabaseModel]:
        """前回と異なるランク情報のみを取得

        Args:
            users_rank (list[ApexUserRankDatabaseModel]): 今回のユーザランク情報

        Returns:
            list[ApexUserRankDatabaseModel]: 更新のあったランク情報
        """
        if self.__prev_update_user_ranks is None:
            self.store_prev_users_rank(users_rank)
            return users_rank
        
        changed_users_rank = [user for user in users_rank if not user in self.__prev_update_user_ranks]
        self.store_prev_users_rank(users_rank)

        return changed_users_rank

    async def refresh_apex_user_rank(self, uid: int) -> Union[ApexUserRankModel, ApexUserRankDatabaseModel, None]:
        """データベースに登録済みの追跡対象ユーザのランク情報を取得して登録
        """
        user = None
        with DatabaseApexUserUrility() as database:
            user = database.select_by_uid(uid=uid)

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