from typing import Union
from models.bot.apex_user_model import ApexUserModel
from models.bot.apex_user_rank_model import ApexUserRankModel
from models.database.apex_user_database_model import ApexUserDatabaseModel
from utilities.database.database import DatabaseUtility
import utilities.database.sql as sql


class DatabaseApexUserUrility(DatabaseUtility):
    # SELECT
    def select_users(self) -> list[dict]:
        with self.connection.cursor() as cursor:
            cursor.execute(sql.SELECT_APEX_USERS)
            result = cursor.fetchall()
            return result

    def select_by_uid(self, uid: int = None, apex_user: Union[ApexUserModel, ApexUserRankModel] = None) -> ApexUserDatabaseModel:
        with self.connection.cursor() as cursor:
            if not uid is None:
                cursor.execute(sql.SELECT_APEX_USER_BY_UID, {'uid': uid})
            else:
                cursor.execute(sql.SELECT_APEX_USER_BY_UID, apex_user.database_dict)
            result = cursor.fetchone()
            user = ApexUserDatabaseModel(result)
            return user

    # UPDATE
    def update_by_uid(self, apex_user: Union[ApexUserModel, ApexUserRankModel]):
        with self.connection.cursor() as cursor:
            cursor.execute(sql.UPDATE_APEX_USER_BY_UID, apex_user.database_dict)
        self.commit()

    def update_by_name(self, apex_user: Union[ApexUserModel, ApexUserRankModel]):
        with self.connection.cursor() as cursor:
            cursor.execute(sql.UPDATE_APEX_USER_BY_NAME, apex_user.database_dict)
        self.commit()

    def update_icon_url_by_uid(self, apex_user: Union[ApexUserModel, ApexUserRankModel], icon_url: str):
        with self.connection.cursor() as cursor:
            cursor.execute(sql.UPDATE_APEX_USER_ICON_BY_UID, {'uid': apex_user.uid, 'icon_url': icon_url})
        self.commit()

    # DELETE
    def delete_by_uid(self, apex_user: Union[ApexUserModel, ApexUserRankModel, ApexUserDatabaseModel]):
        with self.connection.cursor() as cursor:
            cursor.execute(sql.DELETE_APEX_USER_BY_UID, apex_user.database_dict)
        self.commit()

    def delete_name(self, apex_user: Union[ApexUserModel, ApexUserRankModel, ApexUserDatabaseModel]):
        with self.connection.cursor() as cursor:
            cursor.execute(sql.DELETE_APEX_USER_BY_NAME, apex_user.database_dict)
        self.commit()