import os
from contextlib import contextmanager
from clipsai import MediaEditor, AudioVideoFile, Crops, resize

from abstractions.IVideoResizer import IVideoResizer
from utils.Logger import Logger
from utils.utils import PYANNOTE_TOKEN


@contextmanager
def suppress_output():
    with open(os.devnull, "w") as devnull:
        stdout_fd = os.dup(1)
        stderr_fd = os.dup(2)
        try:
            os.dup2(devnull.fileno(), 1)
            os.dup2(devnull.fileno(), 2)
            yield
        finally:
            os.dup2(stdout_fd, 1)
            os.dup2(stderr_fd, 2)
            os.close(stdout_fd)
            os.close(stderr_fd)


class VideoResizer(IVideoResizer):
    def __init__(
        self,
        media_editor: MediaEditor,
        logger: Logger,
        face_margin: int,
        aspect_ratio: tuple[int, int],
        device: str,
    ):
        self._media_editor = media_editor
        self._logger = logger
        self._face_margin = face_margin
        self._aspect_ratio = aspect_ratio
        self._device = device

    def resize(self, file_path: str):
        media_file = AudioVideoFile(file_path)

        self._logger.info(f"Resizing video to {self._aspect_ratio}")
        self._logger.info(f"Face margin: {self._face_margin}px")

        with suppress_output():
            crops = self.__calculate_crops(
                file_path=file_path,
                original_width=media_file.get_width_pixels(),
            )
            temp_file_path = file_path.replace(".mp4", "_temp.mp4")

            self._media_editor.resize_video(
                original_video_file=media_file,
                resized_video_file_path=temp_file_path,
                width=crops.crop_width,
                height=crops.crop_height,
                segments=crops.to_dict()["segments"],
            )

            os.replace(temp_file_path, file_path)

    def __calculate_crops(
        self,
        file_path: str,
        original_width: int,
    ) -> Crops:
        return resize(
            video_file_path=file_path,
            pyannote_auth_token=PYANNOTE_TOKEN,
            face_detect_width=original_width,
            face_detect_margin=self._face_margin,
            aspect_ratio=self._aspect_ratio,
            device=self._device,
        )
