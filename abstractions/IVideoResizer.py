from abc import abstractmethod


class IVideoResizer:
    @abstractmethod
    def resize(self, file_path: str):
        pass
