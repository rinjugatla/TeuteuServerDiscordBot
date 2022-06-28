from models.bot.apex_user_rank_model import ApexUserRankModel
from utilities.database.database import DatabaseUtility
import utilities.database.sql as sql


class DatabaseApexUserRankUrility(DatabaseUtility):
    # SELECT
    def select_ranks(self) -> list[dict]:
        with self.connection.cursor() as cursor:
            cursor.execute(sql.SELECT_APEX_USER_RANKS)
            result = cursor.fetchall()
            return result

    def select_by_user_uid(self, uid: int, limit: int = 100) -> list[dict]:
        with self.connection.cursor() as cursor:
            cursor.execute(sql.SELECT_APEX_USER_RANK_BY_UID, {'uid': uid, 'limit': limit})
            result = cursor.fetchall()
            return result

    def select_by_users_uid(self, uids: list[int], limit: int = 100) -> list[list[dict]]:
        ranks = []
        with self.connection.cursor() as cursor:
            for uid in uids:
                cursor.execute(sql.SELECT_APEX_USER_RANK_BY_UID, {'uid': uid, 'limit': limit})
                rank = cursor.fetchall()
                ranks.append(rank)
        return ranks

    def select_by_user_name(self, name: int, limit: int = 100) -> list[dict]:
        with self.connection.cursor() as cursor:
            cursor.execute(sql.SELECT_APEX_USER_RANK_BY_NAME, {'name': name, 'limit': limit})
            result = cursor.fetchall()
            return result
    
    # INESRT
    def insert_rank_by_uid(self, user_rank: ApexUserRankModel) -> bool:
        result = self.insert_ranks_by_uid([user_rank])
        return result

    def insert_ranks_by_uid(self, user_ranks: list[ApexUserRankModel]) -> bool:
        if user_ranks is None:
            return False
        with self.connection.cursor() as cursor:
            for user_rank in user_ranks:
                if user_rank is None:
                    continue
                cursor.execute(sql.INSERT_APEX_USER_RANK_BY_UID, user_rank.database_dict)
            self.commit()
        return True
    
    def insert_rank_by_name(self, user_rank: ApexUserRankModel) -> bool:
        result = self.insert_ranks_by_name([user_rank])
        return result

    def insert_ranks_by_name(self, user_ranks: list[ApexUserRankModel]) -> bool:
        if user_ranks is None:
            return False
        with self.connection.cursor() as cursor:
            for user_rank in user_ranks:
                if user_rank is None:
                    continue
                cursor.execute(sql.INSERT_APEX_USER_RANK_BY_NAME, user_rank.database_dict)
            self.commit()
        return True