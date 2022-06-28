from models.database.apex_user_database_model import ApexUserDatabaseModel


class ApexUserRankDatabaseModel(ApexUserDatabaseModel):
    def __init__(self, rank: dict):
        super().__init__(rank)
        self.__parse(rank)

    def __str__(self) -> str:
        return '未実装'

    def __parse(self, rank: dict):
        self.__id: int = rank['id']
        self.__apex_user_id: int = rank['apex_user_id']
        self.__season: int = rank['season']
        self.__split: int = rank['split']
        self.__battle = {
            'score': rank['battle_score'],
            'name': rank['battle_name'],
            'division': rank['battle_division']
        }
        self.__arena = {
            'score': rank['arena_score'],
            'name': rank['arena_name'],
            'division': rank['arena_division']
        }

    @property
    def id(self) -> int:
        return self.__id

    @property
    def season(self) -> int:
        return self.__season

    @property
    def split(self) -> int:
        return self.__split

    # battle
    @property
    def battle(self) -> dict:
        return self.__battle

    @property
    def battle_score(self) -> int:
        return self.__battle['score']

    @property
    def battle_name(self) -> str:
        return self.__battle['name']

    @property
    def battle_division(self) -> int:
        return self.__battle['division']

    # arena
    @property
    def arena(self) -> dict:
        return self.__arena

    @property
    def arena_score(self) -> int:
        return self.__arena['score']

    @property
    def arena_name(self) -> str:
        return self.__arena['name']

    @property
    def arena_division(self) -> int:
        return self.__arena['division']