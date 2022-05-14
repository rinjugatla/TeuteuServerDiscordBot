from typing import Union

from discord import VoiceClient
from discord.player import FFmpegPCMAudio
from models.voice_client_model import VoiceClientModel


class VoiceClientController(VoiceClientModel):
    def __init__(self, client: Union[VoiceClient, None] = None):
        super().__init__(client)

    def update(self, client: VoiceClient):
        self.voice_client = client

    def play(self, filename: str):
        if not self.is_connected:
            return
        if filename is None or len(filename) == 0:
            return
        
        self.voice_client.play(FFmpegPCMAudio(filename))

    def send_audio_packet(self, data: bytes, encode: bool):
        if not self.is_connected:
            return
        self.voice_client.send_audio_packet(data=data, encode=encode)

    def pause(self):
        self.voice_client.pause()

    def resume(self):
        if self.voice_client.is_paused:
            self.voice_client.resume()

    def stop(self):
        self.voice_client.stop()

    async def disconnect(self):
        if self.is_connected:
            await self.voice_client.disconnect()
            self.voice_client = None