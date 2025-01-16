from abc import abstractmethod


class IVideoScaler:
    @abstractmethod
    def scale(self, file_path: str):
        pass
