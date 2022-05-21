class ApexUserModel():
    def __init__(self, data: dict):
        self.__parse(data)

    def __parse(self, data: dict):
        data_global = data['global'] if 'global' in data else None
        if data_global is None:
            return

        self.__level = data_global['level'] if 'level' in data_global else -1
        self.__name = data_global['name'] if 'name' in data_global else ''
        self.__uid = data_global['uid'] if 'uid' in data_global else -1
        self.__platform = data_global['platform'] if 'platform' in data_global else ''

    def __str__(self) -> str:
        return f'level: {self.level}\nname: {self.name}\nuid: {self.uid}\nplatform: {self.platform}'

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
    def database_dict(self) -> dict:
        return {
            'level': self.level,
            'name': self.name,
            'uid': self.uid,
            'platform': self.platform
        }