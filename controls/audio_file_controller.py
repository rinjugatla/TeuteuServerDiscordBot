from typing import Union
from models.audio_file_model import AudioFileModel


class AudioFileController():
    def __init__(self) -> None:
        self.__files: list[AudioFileModel] = []

    def __str__(self) -> str:
        text = ''
        for file in self.__files:
            text += f'{file}\n'
        return f'{text}'

    def to_list(self) -> list[AudioFileModel]:
        return list(self.__files)

    def append(self, audio_model: AudioFileModel):
        if self.is_exist(audio_model):
            return
        self.__files.append(audio_model)

    def remove(self, audio_model: AudioFileModel):
        if not self.is_exist(audio_model):
            return
        self.__files.remove(audio_model)

    def is_exist(self, audio_model: AudioFileModel) -> bool:
        if audio_model is None:
            return False
        is_exist = audio_model in self.__files
        return is_exist

    def get_by_filename(self, filename: str) -> Union[AudioFileModel, None]:
        files = [file for file in self.__files if file.filename == filename]
        if not files or len(files) == 0:
            return None
        return files[0]

    def get(self, other_file: AudioFileModel) -> Union[AudioFileModel, None]:
        files = [file for file in self.__files if file == other_file]
        if not files or len(files) == 0:
            return None
        return files[0]