class ApexUserDatabaseModel():
    def __init__(self, user: dict):
        self.__parse(user)

    def __str__(self) -> str:
        return f'id: {self.id}\nlevel: {self.level}\nname: {self.name}\nuid: {self.uid}\nplatform: {self.platform}'

    def summary(self) -> str:
        return f'level {self.level} {self.name}({self.uid})'

    def __parse(self, user: dict):
        self.__id: int = user['id']
        self.__level: int = user['level']
        self.__name: str = user['name']
        self.__uid: int = user['uid']
        self.__platform: str = user['platform']
        self.__icon_url: str = user['icon_url']

    @property
    def id(self) -> int:
        return self.__id

    @property
    def level(self) -> int:
        return self.__level
    
    @property
    def name(self) -> str:
        return self.__name

    @property
    def uid(self) -> int:
        return self.__uid

    @property
    def platform(self) -> str:
        return self.__platform

    @property
    def icon_url(self) -> str:
        return self.__icon_url

    @property
    def database_dict(self) -> dict:
        return {
            'id': self.id,
            'level': self.level,
            'name': self.name,
            'uid': self.uid,
            'platform': self.platform,
            'icon_url': self.icon_url,
        }