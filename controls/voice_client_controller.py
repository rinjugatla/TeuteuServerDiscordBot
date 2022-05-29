import asyncio
from typing import Union

from discord import VoiceChannel, VoiceClient
from discord.player import FFmpegPCMAudio
from controls.audio_queue_controller import AudioQueueController
from models.voice_client_model import VoiceClientModel


class VoiceClientController(VoiceClientModel):
    def __init__(self, client: Union[VoiceClient, None] = None):
        super().__init__(client)
        self.__queue_controller = AudioQueueController()
        self.__playing = asyncio.Event()
        asyncio.create_task(self.playing_task())

    def update(self, client: VoiceClient):
        self.voice_client = client

    async def append_audio(self, filepath: str):
        """キューに音声ファイルを追加

        Args:
            filepath (str): 音声ファイルパス
        """
        await self.__queue_controller.put(filepath)

    async def playing_task(self):
        """音声ファイルを再生
        """
        while True:
            self.__playing.clear()
            if self.__queue_controller.empty():
                await asyncio.sleep(0.5)
                continue
            try:
                filepath = await asyncio.wait_for(self.__queue_controller.get(), timeout = 100)
                await self.play(filepath)
            except asyncio.TimeoutError:
                asyncio.create_task(self.disconnect())

    async def play(self, filename: str):
        if not self.is_connected:
            return
        if filename is None or len(filename) == 0:
            return
        
        self.voice_client.play(FFmpegPCMAudio(filename), after = self.play_next)
        await self.__playing.wait()

    def play_next(self, err=None):
        """次のキューの音声を再生

        Args:
            err (_type_, optional): _description_. Defaults to None.
        """
        self.__playing.set()
        return

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

    @property
    def member_count(self) -> Union[int, None]:
        """チャンネル参加人数
        """
        if not self.is_connected:
            return None
        
        channel: VoiceChannel = self.voice_client.channel
        count = len(channel.members)
        return count

    async def disconnect(self):
        """VCから切断
        """
        self.__queue_controller.clear()
        if self.is_connected:
            await self.voice_client.disconnect()
            self.voice_client = None