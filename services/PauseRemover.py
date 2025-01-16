import os

from moviepy import VideoFileClip, concatenate_videoclips

from abstractions.IPauseRemover import IPauseRemover
from utils.Logger import Logger


class PauseRemover(IPauseRemover):
    def __init__(self, buffer_time: float, logger: Logger):
        self._buffer_time = buffer_time
        self._logger = logger

    def remove_pauses(self, file_path: str, subtitles: list):
        video = VideoFileClip(file_path)

        self._logger.info(f"Original video duration: {video.duration}")
        self._logger.info(f"Buffer time: {self._buffer_time}")

        segments = []
        prev_end = 0

        for (start, end), _ in subtitles:
            adjusted_start = max(0, start - self._buffer_time)
            adjusted_end = min(video.duration, end + self._buffer_time)

            if adjusted_start < prev_end:
                adjusted_start = prev_end

            segments.append((adjusted_start, adjusted_end))
            prev_end = adjusted_end

        self._logger.info(f"Found {len(segments) - 1} pauses")
        clips = [video.subclipped(start, end) for start, end in segments if start < end]
        final_video = concatenate_videoclips(clips)

        self._logger.info(f"New video duration: {round(final_video.duration)}")

        output_path = file_path.replace(".mp4", "_no_pauses.mp4")
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        os.replace(output_path, file_path)
