from typing import Union
import google.auth, google.auth.transport.requests
import os, json, aiohttp, base64, re
from controls.audio_management_contoller import AudioManagementController
from controls.voice_client_controller import VoiceClientController
from utilities.log import LogUtility
from discord import ApplicationContext, Client, Guild, Member, Message, SlashCommandGroup, VoiceState, TextChannel, VoiceChannel
from discord.ext import  tasks
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
        self.url = 'https://texttospeech.googleapis.com/v1beta1/text:synthesize'
        self.text_limit_count = 100 # 読み上げ長さ
        self.message_author_name_limit = 5 #　メッセージ送信者名読み上げ長さ

    tts_command_group = SlashCommandGroup("tts", "文字読み上げ")

    @Cog.listener(name='on_ready')
    async def on_ready(self):
        if not self.is_on_ready:
            self.update_gcp_info.start()
            self.voice_controller = VoiceClientController()
            self.is_on_ready = True

    @tasks.loop(minutes=30)
    async def update_gcp_info(self):
        """n分毎にGCPアクセストークンを更新
        """
        self.gcp_token = self.get_gcp_token()
        self.gcp_headers = {
            'Authorization': f"Bearer {self.gcp_token}",
            'X-Goog-User-Project': const.GCP_PROJECT,
            'Content-Type': 'application/json; charset=utf-8',
        }
        LogUtility.print('GCPトークン更新完了')

    def get_gcp_token(self):
        """GCPアクセストークン取得
        
        あらかじめ環境変数`GOOGLE_APPLICATION_CREDENTIALS`に認証情報ファイルを設定すること
        """
        creds, project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        token = creds.token
        return token

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
        await context.respond('ボイスチャンネルから切断しました。')

    @Cog.listener(name='on_voice_state_update')
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        count = self.voice_controller.member_count
        if count is None:
            return
        if count == 1:
            self.enter_text_channel = None
            await self.voice_controller.disconnect()

        # 他のBOTと同居させない
        exists_other_bot = self.exists_bot_in_voice_channel(self.voice_controller.voice_channel)
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

        validated_text = self.create_speech_text(message)
        filepath = self.audio_controller.load_audio(validated_text)
        if not filepath is None:
            LogUtility.print_green(f'[GCP]音声データをローカルファイルから取得 {self.create_preview_text(validated_text)}')
            await self.voice_controller.append_audio(filepath)
            return

        speech_data = await self.request_text_to_speech(message.guild, validated_text)
        if speech_data == None:
            LogUtility.print_red('データが不正なため読み上げ終了')
            return
        filepath = self.audio_controller.save_audio(validated_text, speech_data)
        await self.voice_controller.append_audio(filepath)

    def create_speech_text(self, message: Message) -> str:
        """読み上げメッセージを作成

        Returns:
            str: メッセージ発信者 + 補正済みのメッセージ
        """
        author = message.author.name[:self.message_author_name_limit]
        # 名前とメッセージの間に余裕を持たせるため「。」を使用
        text = f'{author}。{message.content}'
        validated_text = self.validate_text(message.guild, text)
        return validated_text

    async def request_text_to_speech(self, guild: Guild, text: str) -> Union[bytes, None]:
        LogUtility.print_green(f'[GCP]音声データを取得 {text}')
        async with aiohttp.ClientSession() as session:
            payload_json = self.create_payload(text)
            async with session.post(url=self.url, data=payload_json, headers=self.gcp_headers) as response:
                if response.status != 200:
                    LogUtility.print_red(f'[GCP]音声データの取得に失敗 {response.content}')
                    return None

                data = await response.json()
                if 'audioContent' in data:
                    return base64.b64decode(data['audioContent'])
                LogUtility.print_red(f'[GCP]音声データにaudioContent要素なし {data}')
                return None

    def create_preview_text(self, text: str) -> str:
        preview = text if len(text) < 110 else f'{text[:100]}...{text[-10:]}'
        return preview

    def create_payload(self, text: str, speed: float = 1.0, pitch: float = 0) -> str:
        payload = {
            "audioConfig": {
                "audioEncoding": "OGG_OPUS" if self.use_ogg else "LINEAR16",
                "pitch": pitch,
                "speakingRate": speed
            },
            "input": {
                "text": text
            },
            "voice": {
                "languageCode": "ja-JP",
                "name": "ja-JP-Wavenet-B"
            }
        }

        return json.dumps(payload, ensure_ascii=False)

    def validate_text(self, guild: Guild, text: str) -> str:
        """URlやメンションを
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
        pattern = r'(https?:\/\/(?P<domain>[^/]+)/[\w\/:%#\$&\?\(\)~\.,=\+\-]+)'
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
