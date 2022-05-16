import hashlib, time, os


class AudioFileModel():
    def __init__(self, text: str = None, extension: str = None, filename: str = None, unixtime: int = int(time.time())):
        """_summary_

        Args:
            text (str): 音声ファイルの内容
            extension (str): 拡張子
            filename (str): ファイル名を直接指定する場合はこちらを使用. Defaults to None.
            unixtime (int, optional): 音声ファイルの作成日時. Defaults to int(time.time()).
        """
        if filename is None:
            self.__hash = AudioFileModel.get_hash(text)
            self.__extension = extension
        else:
            # ファイル名がハッシュと一致
            filename_ext = os.path.splitext(os.path.basename(filename))
            self.__hash = filename_ext[0]
            # .ext形式なので「.」を除去
            self.__extension = filename_ext[1][1:]
        self.__unixtime = unixtime

    def __str__(self) -> str:
        return f'{self.filename} {self.__unixtime}'

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, AudioFileModel):
            return self.filename == __o.filename
        return False

    @staticmethod
    def get_hash(text: str) -> str:
        hash = hashlib.sha256(text.encode()).hexdigest()
        return hash

    @property
    def filename(self):
        return f'{self.__hash}.{self.__extension}'

    def create_at(self):
        return self.__unixtime