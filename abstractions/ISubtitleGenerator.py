from abc import abstractmethod


class ISubtitleGenerator:
    @abstractmethod
    def add_subtitles(self, file_path: str) -> list:
        pass
