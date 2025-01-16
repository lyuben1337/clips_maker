from abc import abstractmethod
from clipsai import Transcription, Clip


class IVideoTrimmer:
    @abstractmethod
    def trim_clips(self, transcription: Transcription, file_path: str) -> list[str]:
        pass
