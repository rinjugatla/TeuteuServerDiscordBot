from datetime import datetime
from typing import Union
import google.auth, google.auth.transport.requests
import os, json, aiohttp, base64, re
from controls.audio_management_contoller import AudioManagementController
from controls.voice_client_controller import VoiceClientController
from utilities.log import LogUtility
from discord import ApplicationContext, Client, Guild, Member, Message, SlashCommandGroup, VoiceState, TextChannel, VoiceChannel
from discord.ext import  tasks
from discord.commands import Option
from discord.ext.commands import Cog
if os.path.exists('pro.mode'):
    import secret.secret_pro as secret
    import secret.const_pro as const
else:
    import secret.secret_dev as secret
    import secret.const_dev as const


class TextToSpeech(Cog):
    def __init__(self, bot: Client):
        self.bot = bot
        self.is_on_ready = False
        self.use_ogg = True
        self.enter_text_channel : TextChannel = None # 接続コマンドを実行したチャンネル
        self.voice_controller = None
        self.audio_controller = AudioManagementController(use_ogg=self.use_ogg)
        self.audio_query_url = 'http://localhost:50021/audio_query'
        self.synthesis_url = 'http://localhost:50021/synthesis'
        self.text_limit_count = 100 # 読み上げ長さ
        self.message_author_name_limit = 6 #　メッセージ送信者名読み上げ長さ
        self.last_speech_interval_sec = 60 * 3 # メッセージ読み上げに送信者名を付与しない時間
        self.last_speech_datetime = datetime.now()
        self.last_speech_author = ""
        self.speaker_id = 1 # idはhttp://localhost:50021/speakersを参照

    tts_command_group = SlashCommandGroup("tts", "文字読み上げ")

    @Cog.listener(name='on_ready')
    async def on_ready(self):
        if not self.is_on_ready:
            self.voice_controller = VoiceClientController()
            self.is_on_ready = True

    def is_valid(self, message: Message):
        if message.author.bot:
            return False
        if len(message.content) == 0 or message.content[0] == const.COMMAND_PREFIX:
            return False
        return True

    @tts_command_group.command(name='connect', description='ボイスチャンネルに接続')
    async def command_connect(self, context: ApplicationContext):
        if context.author.voice == None:
            await context.respond('ボイスチャンネルに接続して使用してください。')
            return
            
        if self.voice_controller.is_connected:
            await context.respond('すでにVCに参加済みです。')
            return

        voice_channel = context.author.voice.channel
        exists_other_bot = self.exists_other_bot_in_voice_channel(voice_channel)
        if exists_other_bot:
            await context.respond('すでに他のBOTが参加済みです。')
            return
        
        voice_client = await voice_channel.connect()
        self.voice_controller.update(voice_client)
        self.enter_text_channel = context.channel
        await context.respond('ボイスチャンネルに接続しました。')

    @tts_command_group.command(name='disconnect', description='ボイスチャンネルから切断')
    async def command_disconnect(self, context: ApplicationContext):
        await self.voice_controller.disconnect()
        self.enter_text_channel = None
        self.init_last_speech_author()
        await context.respond('ボイスチャンネルから切断しました。')

    @tts_command_group.command(name='change_speaker', description='ボイスを変更')
    async def command_disconnect(self, context: ApplicationContext, 
        id: Option(int, 'ID', required=True)):
        await context.defer()
        if id is None or not(0 <= id <= 38):
            await context.respond('idは0~38の整数で指定してください。')
        
        await context.respond(f'ボイス{self.speaker_id}から{id}に変更しました。')
        self.speaker_id = id

    @Cog.listener(name='on_voice_state_update')
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        count = self.voice_controller.member_count
        if count is None:
            return
        is_onyl_self = count == 1
        if is_onyl_self:
            self.enter_text_channel = None
            await self.voice_controller.disconnect()
            return

        # 他のBOTと同居させない
        exists_other_bot = self.exists_other_bot_in_voice_channel(self.voice_controller.voice_channel)
        if not exists_other_bot:
            return

        await self.enter_text_channel.send('他のBOTが参加したためボイスチャンネルから切断しました。')
        self.enter_text_channel = None
        await self.voice_controller.disconnect()

    def exists_other_bot_in_voice_channel(self, channel: VoiceChannel) -> bool:
        """ボイスチャンネルに他のBOTが接続済みか

        Args:
            channel (VoiceChannel): ボイスチャンネル
        """
        if channel is None:
            return False

        for member in channel.members:
            if member.id == self.bot.user.id:
                continue
            if member.bot:
                return True
        return False

    @Cog.listener(name='on_message')
    async def on_message(self, message: Message):
        """メッセージ検知
        """
        if not self.is_valid(message):
            return

        if not self.voice_controller.is_connected:
            return

        author = self.get_speech_author(message)
        validated_text, use_author = self.create_speech_text(message, author)
        filepath = self.audio_controller.load_audio(validated_text)
        if not filepath is None:
            LogUtility.print_green(f'[VOICEVOX]音声データをローカルファイルから取得 {self.create_preview_text(validated_text)}')
            await self.voice_controller.append_audio(filepath)
            return

        speech_data = await self.request_text_to_speech(message.guild, validated_text)
        if speech_data is None:
            LogUtility.print_red('データが不正なため読み上げ終了')
            return
        
        if use_author:
            self.store_last_speech_author(author)
        
        filepath = self.audio_controller.save_audio(validated_text, speech_data)
        await self.voice_controller.append_audio(filepath)

    def create_preview_text(self, text: str) -> str:
        preview = text if len(text) < 110 else f'{text[:100]}...{text[-10:]}'
        return preview

    def create_speech_text(self, message: Message, author: str) -> tuple[str, bool]:
        """読み上げメッセージを作成
           前回の発言者と同じ発言者の場合は発言者名をメッセージに含めない

        Args:
            message (Message): メッセージ
            author (str): メッセージの発言者(補正済み)

        Returns:
            str: 補正済みのメッセージ
        """
        same_author = self.last_speech_author == author
        is_over_interval = (datetime.now() - self.last_speech_datetime).seconds > self.last_speech_interval_sec
        use_author = not same_author or is_over_interval

        if use_author:
            # 名前とメッセージの間に余裕を持たせるため「。」を使用
            text = f'{author}。{message.content}'
        else:
            text = message.content
            
        validated_text = self.validate_text(message.guild, text)
        return (validated_text, use_author)

    def get_speech_author(self, message: Message) -> str:
        """テキストを送ったユーザ名を補正して取得
        """
        if message is None:
            return None
        author = message.author.name[:self.message_author_name_limit]
        return author

    def store_last_speech_author(self, author: str):
        if author is not None:
            self.last_speech_datetime = datetime.now()
            self.last_speech_author = author
    
    def init_last_speech_author(self):
        self.last_speech_datetime = datetime.now()
        self.last_speech_author = ""

    async def request_text_to_speech(self, guild: Guild, text: str) -> Union[bytes, None]:
        """GCPのTTSサービスでテキストをオーディオに変換
        """
        LogUtility.print_green(f'[VOICEVOX]音声データを取得 {text}')
        query = await self.request_audio_query(text)
        if query is None:
            return

        audio_data = await self.request_synthesis(query)
        return audio_data

    async def request_audio_query(self, text: str) -> str:
        """音声合成用のクエリを作成

        Args:
            text (str): 解析文字列

        Returns:
            str: 音声合成用データ(json)
        """
        async with aiohttp.ClientSession() as session:
            params = {
                "text": text,
                "speaker": self.speaker_id
            }
            async with session.post(url=self.audio_query_url, params=params) as response:
                if response.status != 200:
                    LogUtility.print_red(f'[VOICEVOX]音声データの取得に失敗 {response.content}')
                    return None

                query = await response.json()
                return query

    async def request_synthesis(self, query_json: str) -> bytes:
        async with aiohttp.ClientSession() as session:
            params = {
                "speaker": self.speaker_id
            }
            async with session.post(url=self.synthesis_url, params=params, json=query_json) as response:
                if response.status != 200:
                    LogUtility.print_red(f'[VOICEVOX]音声データの取得に失敗 {response.content}')
                    return None

                audio = await response.read()
                return audio

    def validate_text(self, guild: Guild, text: str) -> str:
        """URlやメンションを置き換え
        """
        validated = self.replace_url(text)
        validated = self.limit_text(validated)
        validated = self.replace_role(guild, validated)
        validated = self.replace_member(guild, validated)
        validated = self.replace_channel(guild, validated)
        if text != validated:
            LogUtility.print_green(f'[TTS]メッセージを修正 {validated}')
        return validated

    def replace_url(self, text: str) -> str:
        """URLを補正

           http://aaa.bbb/         から aaa URLに修正
           http://aaa.bbb.ccc/hoge から bbb URLに修正
        """
        pattern = r'(https?:\/\/(?P<domain>[^/]+)/[\w\/:%#\$&\?\(\)~\.,=\+\-]*)'
        matchs = re.findall(pattern, text)

        replaced = text
        for match in matchs:
            url = match[0]
            domain = match[1]
            domains = domain.split('.')

            domain_count = len(domains)
            if domain_count == 2:
                main_domanin = domains[0]
            else:
                main_domanin = domains[1]
            replaced = replaced.replace(url, f'{main_domanin} URL')

        return replaced

    def limit_text(self, text: str) -> str:
        """読み上げ文字数を制限
        """
        return text[:self.text_limit_count]

    def replace_role(self, guild: Guild, text: str) -> str:
        """ロールIDをロール名に修正

            <@&12345567> を ロール名 に置き換え
        """
        # [('<@&883972996883181568>', '883972996883181568'), ...]
        pattern = r'(<@&([\d]+)>)'
        role_ids = re.findall(pattern, text)
        validated = text
        for role_id in role_ids:
            id = int(role_id[1])
            name = self.get_role_name_by_id(guild, id)
            validated = validated.replace(role_id[0], '不明なロール' if name is None else name)
            
        return validated

    def get_role_name_by_id(self, guild: Guild, id: int) -> str:
        """ロールIDからロール名を取得
        """
        roles = [role for role in guild.roles if role.id == id]
        if roles is None or len(roles) == 0:
            return None
        return roles[0].name

    def replace_member(self, guild: Guild, text: str) -> str:
        """メンバーIDをメンバー名に修正

            <@1234> を メンバー名 に置き換え
            ニックネームの場合は「@!」<@!1234>
        """
        # [('<@883972996883181568>', '883972996883181568'), ...]
        pattern = r'(<@!?([\d]+)>)'
        member_ids = re.findall(pattern, text)
        validated = text
        for member_id in member_ids:
            id = int(member_id[1])
            name = self.get_member_name_by_id(guild, id)
            validated = validated.replace(member_id[0], '不明なユーザ' if name is None else name)
            
        return validated

    def get_member_name_by_id(self, guild: Guild, id: int) -> str:
        """メンバーIDからメンバー名を取得
        """
        members = [member for member in guild.members if member.id == id]
        if members is None or len(members) == 0:
            return None
        return members[0].name

    def replace_channel(self, guild: Guild, text: str) -> str:
        """チャンネルIDをチャンネル名に修正

            <#1234> を チャンネル名に置き換え
        """
        pattern = r'(<#([\d]+)>)'
        channel_ids = re.findall(pattern, text)
        validated = text
        for channel_id in channel_ids:
            id = int(channel_id[1])
            name = self.get_channel_name_by_id(guild, id)
            validated = validated.replace(channel_id[0], '不明なチャンネル' if name is None else name)
            
        return validated
    
    def get_channel_name_by_id(self, guild: Guild, id: int) -> str:
        """チャンネルIDからチャンネル名を取得
        """
        channels = [channel for channel in guild.channels if channel.id == id]
        if channels is None or len(channels) == 0:
            return None
        return channels[0].name

def setup(bot: Client):
    return bot.add_cog(TextToSpeech(bot))
