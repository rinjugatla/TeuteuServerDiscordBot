import asyncio
import glob
from typing import Union
from controls.audio_file_controller import AudioFileController
from models.audio_file_model import AudioFileModel
from utilities.log import LogUtility

class AudioManagementController():
    def __init__(self, use_ogg: bool = True, audio_dir: str = './audio'):
        """_summary_

        Args:
            use_ogg (bool, optional): ogg形式を使用するか. Defaults to True.
            audio_dir (str, optional): 音声ファイル保存先フォルダ. Defaults to './audio/'.
        """
        self.__use_ogg = use_ogg
        self.__audio_dir = audio_dir
        self.__extension = self.get_extension()
        self.__file_controller = AudioFileController()
        self.load_local_audio()

    def get_extension(self) -> str:
        return 'ogg' if self.__use_ogg else 'wav'

    def load_local_audio(self):
        """ローカルの音声ファイルを取得
        """
        local_files = glob.glob(f'{self.__audio_dir}/*')
        for file in local_files:
            self.__file_controller.append(AudioFileModel(filename=file))
        LogUtility.print('ローカルの音声ファイルを取得', True)
        LogUtility.print(self.__file_controller)

    def get_filepath(self, file: AudioFileModel) -> Union[str, None]:
        if file is None or len(file.filename) == 0:
            return None
        return f'{self.__audio_dir}/{file.filename}'

    def save_audio(self, text:str, data: bytes) -> str:
        """音声ファイルを保存

        Args:
            text (str): 音声の内容

        Returns:
            str: 保存先ファイルパス
        """
        newfile = AudioFileModel(text, self.__extension)
        savepath = self.get_filepath(newfile)
        with open(savepath, "wb") as file:
            file.write(data)
        self.__file_controller.append(newfile)
        return savepath

    def load_audio(self, text: str) -> Union[str, None]:
        """音声ファイルのパスを取得
            存在しない場合はNone
        """
        file_model = AudioFileModel(text, self.__extension)
        file = self.__file_controller.get(file_model)
        if file is None:
            return None
        return self.get_filepath(file)