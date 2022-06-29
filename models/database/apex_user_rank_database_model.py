from __future__ import annotations
from discord import Embed
from models.database.apex_user_database_model import ApexUserDatabaseModel


class ApexUserRankDatabaseModel(ApexUserDatabaseModel):
    def __init__(self, rank: dict):
        super().__init__(rank)
        self.__parse(rank)

    def __str__(self) -> str:
        return '未実装'

    def __parse(self, rank: dict):
        self.__id: int = rank['id']
        self.__season: int = rank['season']
        self.__split: int = rank['split']
        self.__battle = {
            'score': rank['battle_score'],
            'name': rank['battle_name'],
            'division': rank['battle_division'],
            'change': 0
        }
        self.__arena = {
            'score': rank['arena_score'],
            'name': rank['arena_name'],
            'division': rank['arena_division'],
            'change': 0
        }

    def set_change(self, prev: ApexUserRankDatabaseModel):
        """差分を設定

        Args:
            prev (ApexUserRankModel): 前回のランク情報
        """
        self.__battle['change'] = self.battle_score - prev.battle_score
        self.__arena['change'] = self.arena_score - prev.arena_score

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

    @property
    def battle_change(self) -> int:
        return self.__battle['change']

    @property
    def battle_change_str(self) -> str:
        change = self.__battle['change']
        if change == 0:
            return '0'
        elif change > 0:
            return f'+{change}'
        else:
            return f'-{change}'

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
    def arena_change(self) -> int:
        return self.__arena['change']

    @property
    def arena_change_str(self) -> str:
        change = self.__arena['change']
        if change == 0:
            return '0'
        elif change > 0:
            return f'+{change}'
        else:
            return f'-{change}'

    @property
    def arena_stats(self) -> str:
        return f'{self.arena_name} {self.arena_division}({self.arena_score})'

    @property
    def embed(self) -> Embed:
        embed = Embed(
            title=f'{self.name}',
            color=self.embed_color,
        )
        embed.add_field(name='プラットフォーム', value=self.platform)
        embed.add_field(name='レベル', value=self.level)
        embed.add_field(name='UID', value=self.uid)
        embed.add_field(name='バトルロワイヤル', value=f'{self.battle_name} {self.battle_division}')
        embed.add_field(name='スコア', value=self.battle_score)
        embed.add_field(name='前回からの変化', value=self.battle_change_str)
        embed.add_field(name='アリーナ', value=f'{self.arena_name} {self.arena_division}')
        embed.add_field(name='スコア', value=self.arena_score)
        embed.add_field(name='前回からの変化', value=self.arena_change_str)
        return embed

    @property
    def embed_color(self) -> int:
        lower = self.battle_name.lower()
        code = '0xffffff'
        if lower == 'bronze':
            code = '0xa06c48'
        elif lower == 'silver':
            code = '0x4c4a4c'
        elif lower == 'gold':
            code = '0xe6b422'
        elif lower == 'platinum':
            code = '0xb2ffff'
        elif lower == 'diamond':
            code = '0x1663a8'
        elif lower == 'master':
            code = '0x7d49b1'
        elif lower == 'predator':
            code = '0xff0000'
        return int(code, 16)