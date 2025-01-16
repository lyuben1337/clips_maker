from abc import abstractmethod


class IFrameRateReducer:
    @abstractmethod
    def reduce(self, file_path: str):
        pass
