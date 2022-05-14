import asyncio
from typing import Union
from discord import VoiceClient


class VoiceClientModel():
    def __init__(self, client: Union[VoiceClient, None] = None):
        self.__voice_client = client
        # self.__plaing = asyncio.Event()

    @property
    def is_connected(self):
        return self.__voice_client != None

    @property
    def voice_client(self):
        return self.__voice_client

    @voice_client.setter
    def voice_client(self, client: Union[VoiceClient, None]):
        self.__voice_client = client
