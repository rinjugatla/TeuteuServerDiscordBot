from typing import Union
import google.auth, google.auth.transport.requests
import os, json, aiohttp, base64
from controls.voice_client_controller import VoiceClientController
from utilities.log import LogUtility
from discord import Client, Message
from discord.ext import commands
from discord.ext.commands import Cog, Context
if os.path.exists('pro.mode'):
    import secret.secret_pro as secret
    import secret.const_pro as const
else:
    import secret.secret_dev as secret
    import secret.const_dev as const


class Patchnote(Cog):
    def __init__(self, bot: Client):
        self.bot = bot
        self.voice_controller = VoiceClientController()
        self.url = 'https://texttospeech.googleapis.com/v1beta1/text:synthesize'
        self.set_gcp_info()

    def set_gcp_info(self):
        self.gcp_token = self.get_gcp_token()
        self.gcp_headers = {
            'Authorization': f"Bearer {self.gcp_token}",
            'X-Goog-User-Project': const.GCP_PROJECT,
            'Content-Type': 'application/json; charset=utf-8',
        }
        LogUtility.print('GCPトークン取得完了')

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
        if message.author.id == self.bot.user.id:
            return False
        if message.content[0] == const.COMMAND_PREFIX:
            return False
        return True

    def is_valid_command(self, message: Message):
        is_valid = (message.author.id != self.bot.user.id)
        return is_valid

    @commands.command(name='jo')
    async def command_join(self, context: Context):
        message = context.message
        if not self.is_valid_command(message):
            return

        if context.author.voice == None:
            await message.channel.send('ボイスチャンネルに接続して使用してください。')
            return
        voice_client = await context.author.voice.channel.connect()
        self.voice_controller.update(voice_client)

    @commands.command(name='dc')
    async def command_disconnect(self, context: Context):
        await self.voice_controller.disconnect()

    @Cog.listener(name='on_message')
    async def on_message(self, message: Message):
        """メッセージ検知
        """
        if not self.is_valid(message):
            return

        speech_data = await self.request_text_to_speech(message)
        if speech_data == None:
            LogUtility.print('データが不正なため読み上げ終了')
            return
        self.voice_controller.send_audio_packet(speech_data, True)

    async def request_text_to_speech(self, message: Message) -> Union[bytes, None]:
        async with aiohttp.ClientSession() as session:
            payload_json = self.create_payload(message.content)
            async with session.post(url=self.url, data=payload_json, headers=self.gcp_headers) as response:
                if response.status != 200:
                    return None

                data = await response.json()
                if 'audioContent' in data:
                    return base64.b64decode(data['audioContent'])
                return None

    def create_payload(self, text: str, speed: float = 1.0, pitch: float = 0) -> str:
        LogUtility.print(f'{text} {speed} {pitch}')
        payload = {
            "audioConfig": {
                "audioEncoding": "OGG_OPUS",
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


def setup(bot: Client):
    return bot.add_cog(Patchnote(bot))
