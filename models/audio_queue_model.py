import asyncio
from itertools import count
from typing import Union


class AudioQueueModel(asyncio.Queue):
    def __init__(self):
        super().__init__(0)

    @property
    def count(self):
        return len(self._queue)

    def __getitem__(self, index):
        if len(self._queue) > index:
            return None
        return self._queue[index]

    def to_list(self) -> list:
        return list(self._queue)

    def clear(self):
        self._queue.clear()