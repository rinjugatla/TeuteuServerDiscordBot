import datetime
from discord import Message
from pprint import pprint
from discord.ext import commands

RED = '\033[31m'
GREEN = '\033[92m'
BLUE = '\033[94m'
END = '\033[0m'

class LogUtility():
    @staticmethod
    def print_message(messages: list[Message], text: str):
        """Messageからログ出力(:message:を置き換え)

        Args:
            messages (list[Message]): [description]
            text (str): [description]
        """
        if len(messages) == 0:
            return
        for message in messages:
            text = text.replace(':message:', LogUtility.create_message(message), 1)
        LogUtility.print_server(messages[0].guild, text)

    @staticmethod
    def print(text: str, is_print_hr: bool = False):
        if is_print_hr:
            LogUtility.print_hr()
        print(f'[{LogUtility.get_now()}] {text}')

    @staticmethod
    def pprint(text: str):
        pprint(f'[{LogUtility.get_now()}] {text}')

    @staticmethod
    def print_hr():
        print(f'[{LogUtility.get_now()}] --------------------')

    @staticmethod
    def print_login(bot: commands.Bot) -> None:
        """BOTログインログ出力

        Args:
            bot (commands.bot): [description]
        """
        print(f'[{LogUtility.get_now()}] Logged in as {bot.user} ({bot.user.id})')

    def print_red(text: str):
        print(f'[{LogUtility.get_now()}] {RED}{text}{END}')

    def print_green(text: str):
        print(f'[{LogUtility.get_now()}] {GREEN}{text}{END}')

    def print_blue(text: str):
        print(f'[{LogUtility.get_now()}] {BLUE}{text}{END}')
    
    @staticmethod
    def print_error(text: str, description: str, traceback: str):
        """エラーログ出力

        Args:
            text (str): _description_
            description (str): _description_
            traceback (str): _description_
        """
        print(f'[{LogUtility.get_now()}] {RED}[ERROR]{text}{END}\n{description}\n{traceback}')

    @staticmethod
    def get_now() -> str:
        """現在時刻を取得

        Returns:
            str: [description]
        """
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), 'JST'))
        return now.strftime('%Y/%m/%d %H:%M:%S.%f')

    @staticmethod
    def create_message(message: Message) -> str:
        return f'message: {message.jump_url}'