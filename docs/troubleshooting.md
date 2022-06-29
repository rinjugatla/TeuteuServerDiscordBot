# トラブルシューティング

## `GOOGLE_APPLICATION_CREDENTIALS`環境変数が取得できない

* エラーメッセージ

```log
discord.errors.ExtensionFailed: Extension 'cogs.text_to_speech' raised an error: DefaultCredentialsError: Could not automatically determine credentials.
Please set GOOGLE_APPLICATION_CREDENTIALS or explicitly create credentials and re-run the application.
For more information, please see https://cloud.google.com/docs/authentication/getting-started
```

* 環境変数の設定
一応管理者権限で実行
  * コマンドプロンプト
    `set GOOGLE_APPLICATION_CREDENTIALS=C:\tools\gcp\my-key.json`
  * Powershell
    `$env:GOOGLE_APPLICATION_CREDENTIALS="C:\tools\gcp\my-key.json"`

* 環境変数の確認
PC詳細設定から確認しても表示されなかった、Powershellで確認すること。
  * Powershell
    `Get-ChildItem env:`

* 認証が通るか確認
  * Google Cloud SDKから設定が適用されているか確認
    `gcloud auth print-access-token`
  * 認証を通す
    ブラウザでアクセス許可する
    `gcloud auth application-default login`

* 関連情報
  1. [【GCP】環境変数「GOOGLE_APPLICATION_CREDENTIALS」の設定でエラーが発生する](https://qiita.com/sola-msr/items/8d5f4ae6485a8817edfe)
  2. [Google Cloud APIのAccess TokenをPythonで取得する(gcloud auth application-default print-access-tokenのやつ)](https://jpdebug.com/p/1239179)

## 引数の数が違うと言われる

* (最低限)のソースコード

```py
class VoiceClientModel():
    def __init__(self, client: Union[VoiceClient, None] = None):
        self.__voice_client = client

    @property
    def voice_client(self):
        return self.__voice_client

class VoiceClientController(VoiceClientModel):
    def send_audio_packet(self, data: bytes, encode: bool):
        if not self.is_connected:
            return
        self.voice_client.send_audio_packet(data, encode)
```

* エラーメッセージ

```log
Ignoring exception in on_message
Traceback (most recent call last):
  File "C:\workspace\discord\TeuteuServerSupport\venv\lib\site-packages\discord\client.py", line 382, in _run_event
    await coro(*args, **kwargs)
  File "C:\workspace\discord\TeuteuServerSupport\cogs\text_to_speech.py", line 79, in on_message
    self.voice_controller.send_audio_packet(speech_data, True)
  File "C:\workspace\discord\TeuteuServerSupport\controls\voice_client_controller.py", line 17, in send_audio_packet
    self.voice_client.send_audio_packet(data, encode)
TypeError: send_audio_packet() takes 2 positional arguments but 3 were given
```

* 原因
  `Class内メソッドでClass内変数を呼び出す際、暗黙的にSelfが引数が呼ばれている`ため、引数の数が合わずエラーが出ていた

* 対処
  引数を明示的に指定する

```diff
class VoiceClientController(VoiceClientModel):
  def send_audio_packet(self, data: bytes, encode: bool):
      if not self.is_connected:
          return
--      self.voice_client.send_audio_packet(data, encode)
++      self.voice_client.send_audio_packet(data=data, encode=encode)
```

* 関連資料
  1. [Python初心者です。 TypeError: get() takes 2 positional arguments but 3 were givenで困ってます。](https://teratail.com/questions/175406)

## `send_audio_packet`で`AttributeError: 'NoneType' object has no attribute 'encode'`エラー

* エラーメッセージ

```log
Traceback (most recent call last):
  File "c:\workspace\discord\TeuteuServerSupport\venv\lib\site-packages\discord\client.py", line 343, in _run_event
  File "c:\workspace\discord\TeuteuServerSupport\cogs\text_to_speech.py", line 79, in on_message
    self.voice_controller.send_audio_packet(speech_data, True)
  File "c:\workspace\discord\TeuteuServerSupport\controls\voice_client_controller.py", line 17, in send_audio_packet
    self.voice_client.send_audio_packet(data=data, encode=encode)
  File "c:\workspace\discord\TeuteuServerSupport\venv\lib\site-packages\discord\voice_client.py", line 633, in send_audio_packet
    encoded_data = self.encoder.encode(data, self.encoder.SAMPLES_PER_FRAME)
AttributeError: 'NoneType' object has no attribute 'encode'
```

* 原因
  ライブラリの不具合
  `self.encoder`は`play`関数で初めて初期化されるため、これが呼び出されていない場合は`self.encoder`はNoneで初期化されている。

* 対処
  ライブラリを修正

```diff
if encode:
++  if not self.encoder:
++    self.encoder = opus.Encoder()
    encoded_data = self.encoder.encode(data, self.encoder.SAMPLES_PER_FRAME)
else:
    encoded_data = data
packet = self._get_voice_packet(encoded_data)
```

## GCP TTSで`401 Unauthorized`が発生

* エラーメッセージ

```json
{
    "error": {
        "code": 401,
        "message": "Request had invalid authentication credentials. Expected OAuth 2 access token, login cookie or other valid authentication credential. See https://developers.google.com/identity/sign-in/web/devconsole-project.",
        "status": "UNAUTHENTICATED",
        "details": [
            {
                "@type": "type.googleapis.com/google.rpc.ErrorInfo",
                "reason": "ACCESS_TOKEN_EXPIRED",
                "domain": "googleapis.com",
                "metadata": {
                    "service": "texttospeech.googleapis.com",
                    "method": "google.cloud.texttospeech.v1beta1.TextToSpeech.SynthesizeSpeech"
                }
            }
        ]
    }
}
```

* 原因
  アクセストークンの時間切れ

* 対処
  アクセストークン発行から一定時間毎にアクセストークンを発行しなおす

## GAS TTSで403エラーが発生

* エラーメッセージ
  
```log
Your application has authenticated using end user credentials from the Google Cloud SDK or Google Cloud Shell which are not supported by the texttospeech.googleapis.com.
We recommend configuring the billing/quota_project setting in gcloud or using a service account through the auth/impersonate_service_account setting. 
For more information about service accounts and how to use them in your application, see https://cloud.google.com/docs/authentication/.
If you are getting this error with curl or similar tools, you may need to specify 'X-Goog-User-Project' HTTP header for quota and billing purposes.
For more information regarding 'X-Goog-User-Project' header, please check https://cloud.google.com/apis/docs/system-parameters.
```

* 対処
  ヘッダーに`X-Goog-User-Project: project-name`を追加

* 関連情報
  1. [GCP CloudAPIで"We recommend configuring the billing/quota_ project setting"というエラーが出た際の対処法](https://qiita.com/nii_yan/items/3bcd2940e15486b4c6e2)

## SlashCommandの登録で405エラー

* エラーメッセージ

```log
Ignoring exception in on_connect
Traceback (most recent call last):
  File "C:\workspace\discord\TeuteuServerDiscordBot\venv\lib\site-packages\discord\client.py", line 382, in _run_event
  File "C:\workspace\discord\TeuteuServerDiscordBot\venv\lib\site-packages\discord\bot.py", line 1147, in on_connect
    await self.sync_commands()
  File "C:\workspace\discord\TeuteuServerDiscordBot\venv\lib\site-packages\discord\bot.py", line 770, in sync_commands
    await self._bot.http.bulk_upsert_command_permissions(self._bot.user.id, guild_id, guild_cmd_perms)
  File "C:\workspace\discord\TeuteuServerDiscordBot\venv\lib\site-packages\discord\http.py", line 359, in request
    raise HTTPException(response, data)
discord.errors.HTTPException: 405 Method Not Allowed (error code: 0): 405: Method Not Allowed
```

* 対処
  pycordのバージョンを`2.0.0b7`から`2.0.0-rc.1`に変更

## slash_commandの引数のdescriptionを空文字列にするとエラーが発生

* エラーメッセージ

```log
Traceback (most recent call last):
  File "C:\workspace\discord\TeuteuServerDiscordBot\venv\lib\site-packages\discord\cog.py", line 715, in _load_from_module_spec
    spec.loader.exec_module(lib)  # type: ignore
  File "<frozen importlib._bootstrap_external>", line 850, in exec_module
  File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
  File "C:\workspace\discord\TeuteuServerDiscordBot\cogs\apex_stats.py", line 17, in <module>
    class ApexStats(Cog):
  File "C:\workspace\discord\TeuteuServerDiscordBot\cogs\apex_stats.py", line 29, in ApexStats
    async def apex_user(self, context: ApplicationContext,
  File "C:\workspace\discord\TeuteuServerDiscordBot\venv\lib\site-packages\discord\commands\core.py", line 1580, in decorator
    return cls(func, **attrs)
  File "C:\workspace\discord\TeuteuServerDiscordBot\venv\lib\site-packages\discord\commands\core.py", line 644, in __init__
    self.options: List[Option] = self._parse_options(params)
  File "C:\workspace\discord\TeuteuServerDiscordBot\venv\lib\site-packages\discord\commands\core.py", line 707, in _parse_options
    _validate_descriptions(option)
  File "C:\workspace\discord\TeuteuServerDiscordBot\venv\lib\site-packages\discord\commands\core.py", line 163, in _validate_descriptions
    validate_chat_input_description(obj.description)
  File "C:\workspace\discord\TeuteuServerDiscordBot\venv\lib\site-packages\discord\commands\core.py", line 1679, in validate_chat_input_description
    raise error
discord.errors.ValidationError: Command and option description must be 1-100 characters long. Received ""

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\workspace\discord\TeuteuServerDiscordBot\main.py", line 31, in <module>
    bot.start()
  File "C:\workspace\discord\TeuteuServerDiscordBot\main.py", line 27, in start
    self.bot.load_extension(name)
  File "C:\workspace\discord\TeuteuServerDiscordBot\venv\lib\site-packages\discord\cog.py", line 787, in load_extension
    self._load_from_module_spec(spec, name)
  File "C:\workspace\discord\TeuteuServerDiscordBot\venv\lib\site-packages\discord\cog.py", line 718, in _load_from_module_spec
    raise errors.ExtensionFailed(key, e) from e
discord.errors.ExtensionFailed: Extension 'cogs.apex_stats' raised an error: ValidationError: Command and option description must be 1-100 characters long. Received ""
```

* 原因
  slash_commandの引数が正しく与えられていない

* 対処
  引数を正しく与える
  
```diff
    async def apex_user(self, context: ApplicationContext,
--                        action: Option(str, '', choice=['add','remove'], required=True),
++                        action: Option(str, 'hogehoge', choice=['add','remove'], required=True),
                        uid: Option(int, 'UID', required=False),
                        name: Option(str, 'アカウント名', required=False)
                        ):
```

## slash_commandの引数`required = False`が`required = True`よりも前にあるとエラー

* エラーメッセージ

```log
Ignoring exception in on_connect
Traceback (most recent call last):
  File "C:\workspace\discord\TeuteuServerDiscordBot\venv\lib\site-packages\discord\client.py", line 382, in _run_event
    await coro(*args, **kwargs)
  File "C:\workspace\discord\TeuteuServerDiscordBot\venv\lib\site-packages\discord\bot.py", line 1042, in on_connect
    await self.sync_commands()
  File "C:\workspace\discord\TeuteuServerDiscordBot\venv\lib\site-packages\discord\bot.py", line 644, in sync_commands
    registered_guild_commands[guild_id] = await self.register_commands(
  File "C:\workspace\discord\TeuteuServerDiscordBot\venv\lib\site-packages\discord\bot.py", line 529, in register_commands
    registered = await register("bulk", data, _log=False)
  File "C:\workspace\discord\TeuteuServerDiscordBot\venv\lib\site-packages\discord\http.py", line 359, in request
    raise HTTPException(response, data)
discord.errors.HTTPException: 400 Bad Request (error code: 50035): Invalid Form Body
In options.3: Required options must be placed before non-required options
```

* 対処
  `required = True`の引数を先に書く
  
 ```diff
     async def apex_user(self, context: ApplicationContext,
                        action: Option(str, 'アクション名', choice=['add','remove'], required=True),
++                     platform: Option(str, 'プラットフォーム名', choice=['PC', 'PS4', 'X1', 'SWITCH'], required=True),
                        uid: Option(int, 'UID', required=False),
                        name: Option(str, 'アカウント名', required=False),
--                     platform: Option(str, 'プラットフォーム名', choice=['PC', 'PS4', 'X1', 'SWITCH'], required=True)
                        ):
 ```


## 起動時に`discord.errors.HTTPException: 405 Method Not Allowed (error code: 0): 405: Method Not Allowed`エラー発生

* バージョン `bb5b30df4f9bd17ddc075630881de2ef4a7fbd13`

```log
Ignoring exception in on_connect
Traceback (most recent call last):
  File "C:\workspace\discord\TeuteuServerDiscordBotPro\venv\lib\site-packages\discord\client.py", line 382, in _run_event
    await coro(*args, **kwargs)
  File "C:\workspace\discord\TeuteuServerDiscordBotPro\venv\lib\site-packages\discord\bot.py", line 1147, in on_connect
    await self.sync_commands()
  File "C:\workspace\discord\TeuteuServerDiscordBotPro\venv\lib\site-packages\discord\bot.py", line 770, in sync_commands
    await self._bot.http.bulk_upsert_command_permissions(self._bot.user.id, guild_id, guild_cmd_perms)
  File "C:\workspace\discord\TeuteuServerDiscordBotPro\venv\lib\site-packages\discord\http.py", line 359, in request
    raise HTTPException(response, data)
discord.errors.HTTPException: 405 Method Not Allowed (error code: 0): 405: Method Not Allowed
```

* 対処
  pycordのバージョンを`2.0.0b7`から`2.0.0rc1`に更新