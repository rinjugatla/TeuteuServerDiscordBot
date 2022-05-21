import re
from models.bot.apex_user_model import ApexUserModel


class ApexUserRankModel(ApexUserModel):
    def __init__(self, data: dict):
        super().__init__(data)
        self.__parse(data)
        
    def __parse(self, data: dict):
        data_global = data['global'] if 'global' in data else None
        if data_global is None:
            return
        data_rank = data_global['rank'] if 'rank' in data_global else None
        data_arena = data_global['arena'] if 'arena' in data_global else None
        if data_rank is None or data_arena is None:
            return

        self.__parse_season_split(data_rank)
        self.__battle = {
            'score': data_rank['rankScore'],
            'name': data_rank['rankName'],
            'division': data_rank['rankDiv']
        }
        self.__arena = {
            'score': data_arena['rankScore'],
            'name': data_arena['rankName'],
            'division': data_arena['rankDiv']
        }

    def __parse_season_split(self, data_rank: dict):
        """シーズンとスプリットを設定
        """
        pattern = r'season(?P<season>[\d]+)_split_(?P<split>[\d])'
        match = re.match(pattern, data_rank['rankedSeason'])
        if match:
            self.__season = -1
            self.__split = -1
        else:
            self.__season = -1
            self.__split = -1

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

    @property
    def battle_stats(self) -> str:
        return f'{self.battle_name} {self.battle_division}({self.battle_score})'
    
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

    @property
    def arena_stats(self) -> str:
        return f'{self.arena_name} {self.arena_division}({self.arena_score})'

    @property
    def database_dict(self) -> dict:
        result: dict = super().database_dict
        result.update({
            'season': self.season,
            'split': self.split,
            'battle_score': self.battle_score,
            'battle_name': self.battle_name,
            'battle_division': self.battle_division,
            'arena_score': self.arena_score,
            'arena_name': self.arena_name,
            'arena_division': self.arena_division,
        })
        return result