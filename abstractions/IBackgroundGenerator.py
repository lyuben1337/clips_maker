from abc import abstractmethod


class IBackgroundGenerator:
    @abstractmethod
    def add_background(self, file_path: str):
        pass