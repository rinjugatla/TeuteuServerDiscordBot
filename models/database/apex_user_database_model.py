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
        # self.__craeted_at = user['created_at'] if 'created_at' in user else None
        # self.__updated_at = user['updated_at'] if 'updated_at' in user else None

    @property
    def id(self) -> int:
        return self.__id

    @property
    def level(self) -> int:
        return self.__level
    
    @property
    def name(self) -> int:
        return self.__name

    @property
    def uid(self) -> int:
        return self.__uid

    @property
    def platform(self) -> int:
        return self.__platform

    # @property
    # def created_at(self) -> int:
    #     return self.__created_at

    # @property
    # def updated_at(self) -> int:
    #     return self.__updated_at