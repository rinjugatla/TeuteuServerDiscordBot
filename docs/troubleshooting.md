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