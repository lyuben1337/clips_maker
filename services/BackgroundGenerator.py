import os
import cv2
from moviepy import VideoFileClip, CompositeVideoClip
from abstractions.IBackgroundGenerator import IBackgroundGenerator
from utils.Logger import Logger


class BackgroundGenerator(IBackgroundGenerator):
    def __init__(self, logger: Logger, target_height: int = 1920):
        self._target_height = target_height
        self._logger = logger

    def add_background(self, file_path: str):
        clip = VideoFileClip(file_path)
        width, height = clip.size

        self._logger.info(f"Current video resolution: {width}x{height}")

        if height > self._target_height:
            self._logger.info(f"Adding background not possible!")
            return

        scale_factor = self._target_height / height
        target_width = int(width * scale_factor)

        blurred_clip = clip.image_transform(
            lambda frame: BackgroundGenerator.__blur_and_resize_frame(
                frame, target_width, self._target_height
            )
        )

        final_clip = CompositeVideoClip(
            [
                blurred_clip.with_position(("center", "center")),
                clip.with_position(("center", "center")),
            ],
            size=(width, self._target_height),
        )

        temp_file_path = file_path.replace(".mp4", "_temp.mp4")
        final_clip.write_videofile(
            filename=temp_file_path, codec="libx264", audio_codec="aac"
        )
        os.replace(temp_file_path, file_path)

        self._logger.info(
            f"Background added successfully! New resolution: {width}x{self._target_height}"
        )

    @staticmethod
    def __blur_and_resize_frame(frame, target_width, target_height):
        blurred_frame = cv2.GaussianBlur(frame, (51, 51), 0)
        resized_frame = cv2.resize(
            blurred_frame, (target_width, target_height), interpolation=cv2.INTER_LINEAR
        )
        return resized_frame
