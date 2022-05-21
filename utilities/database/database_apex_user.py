from models.bot.apex_user_model import ApexUserModel
from models.bot.apex_user_rank_model import ApexUserRankModel
from utilities.database.database import DatabaseUtility
import utilities.database.sql as sql


class DatabaseApexUserUrility(DatabaseUtility):
    # SELECT
    def select_users(self) -> list[dict]:
        with self.connection.cursor() as cursor:
            cursor.execute(sql.SELECT_APEX_USERS)
            result = cursor.fetchall()
            return result

    def select_by_uid(self, apex_user: ApexUserModel):
        with self.connection.cursor() as cursor:
            cursor.execute(sql.SELECT_APEX_USERS, apex_user.database_dict)
            result = cursor.fetchone()
            return result

    # UPDATE
    def update_by_uid(self, apex_user: ApexUserModel):
        with self.connection.cursor() as cursor:
            cursor.execute(sql.UPDATE_APEX_USER_BY_UID, apex_user.database_dict)
        self.commit()

    def update_by_name(self, apex_user: ApexUserModel):
        with self.connection.cursor() as cursor:
            cursor.execute(sql.UPDATE_APEX_USER_BY_NAME, apex_user.database_dict)
        self.commit()

    # DELETE
    def delete_by_uid(self, apex_user: ApexUserModel):
        with self.connection.cursor() as cursor:
            cursor.execute(sql.DELETE_APEX_USER_BY_UID, apex_user.database_dict)
        self.commit()

    def delete_name(self, apex_user: ApexUserModel):
        with self.connection.cursor() as cursor:
            cursor.execute(sql.DELETE_APEX_USER_BY_NAME, apex_user.database_dict)
        self.commit()