import os
import cv2
from moviepy import VideoFileClip, CompositeVideoClip
from abstractions.IBackgroundGenerator import IBackgroundGenerator
from utils.Logger import Logger


class BackgroundGenerator(IBackgroundGenerator):
    def __init__(self, logger: Logger, target_ratio: tuple[int, int] = (9, 16)):
        self._target_ratio = target_ratio
        self._logger = logger

    def add_background(self, file_path: str):
        clip = VideoFileClip(file_path)
        orig_width, orig_height = clip.size
        target_width, target_height = self._target_ratio
        target_ratio = target_width / target_height

        self._logger.info(f"Current video resolution: {orig_width}x{orig_height}")

        blurred_width = orig_width
        blurred_height = int(orig_width / target_ratio)

        self._logger.info(f"Blurred clip resolution: {blurred_width}x{blurred_height}")

        blurred_clip = clip.image_transform(
            lambda frame: self.__blur_and_resize_frame(
                frame, blurred_width, blurred_height
            )
        )

        final_clip = CompositeVideoClip(
            [
                blurred_clip.with_position(("center", "center")),
                clip.with_position(("center", "center")),
            ],
            size=(orig_width, blurred_height),
        )

        temp_file_path = file_path.replace(".mp4", "_temp.mp4")
        final_clip.write_videofile(
            filename=temp_file_path, codec="libx264", audio_codec="aac"
        )
        os.replace(temp_file_path, file_path)

        self._logger.info(
            f"Background added successfully! New resolution: {orig_width}x{blurred_height}"
        )

    def __blur_and_resize_frame(self, frame, target_width, target_height):
        blurred_frame = cv2.GaussianBlur(frame, (51, 51), 0)
        resized_frame = cv2.resize(
            blurred_frame, (target_width, target_height), interpolation=cv2.INTER_LINEAR
        )

        new_width = int(target_height * self._target_ratio[0] / self._target_ratio[1])
        start_x = target_width - new_width
        cropped_frame = resized_frame[:, start_x : start_x + new_width]

        return cropped_frame
