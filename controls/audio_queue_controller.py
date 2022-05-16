from models.audio_queue_model import AudioQueueModel


class AudioQueueController(AudioQueueModel):
    def __init__(self):
        super().__init__()

    def clear(self):
        super().clear()