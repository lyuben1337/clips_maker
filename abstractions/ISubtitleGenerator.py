from abc import abstractmethod


class ISubtitleGenerator:
    @abstractmethod
    def add_subtitles(self, file_path: str, subtitles: list):
        pass

    def generate_subtitles(self, file_path: str) -> list:
        pass

    def save_to_file(self, file_path: str, subtitles: list):
        pass

    def load_from_file(self, file_path: str) -> list:
        pass
