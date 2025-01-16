from abc import abstractmethod


class IPauseRemover:
    @abstractmethod
    def remove_pauses(self, file_path: str, subtitles: list):
        pass
