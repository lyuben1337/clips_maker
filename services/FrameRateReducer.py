import os

from moviepy import VideoFileClip

from abstractions.IFrameRateReducer import IFrameRateReducer
from utils.Logger import Logger


class FrameRateReducer(IFrameRateReducer):
    def __init__(self, logger: Logger, target_fps: int = 24):
        self._target_fps = target_fps
        self._logger = logger

    def reduce(self, file_path: str):
        clip = VideoFileClip(file_path)
        self._logger.info(f"Current frame rate: {round(clip.fps)}")
        self._logger.info(f"Target frame rate: {self._target_fps}")
        if clip.fps <= self._target_fps:
            self._logger.info(f"Frame rate reducing not needed")
            return

        temp_file_path = file_path.replace(".mp4", "_temp.mp4")
        clip.with_fps(self._target_fps).write_videofile(
            temp_file_path, codec="libx264", audio_codec="aac"
        )
        os.replace(temp_file_path, file_path)

        self._logger.info(f"Frame rate reduced to {self._target_fps}")
