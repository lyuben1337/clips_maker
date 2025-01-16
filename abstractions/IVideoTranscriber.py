from abc import abstractmethod


class IVideoTranscriber:
    @abstractmethod
    def transcribe(
        self,
        audio_file_path: str,
        iso6391_lang_code: str or None = None,
        batch_size: int = 16,
    ):
        pass
