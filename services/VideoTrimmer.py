import os

from clipsai import ClipFinder, Transcription, Clip, AudioVideoFile, MediaEditor

from abstractions.IVideoTrimmer import IVideoTrimmer
from utils.Logger import Logger
from utils.utils import RESULTS_PATH, format_time


class VideoTrimmer(IVideoTrimmer):
    def __init__(
        self,
        media_editor: MediaEditor,
        clip_finder: ClipFinder,
        logger: Logger,
        min_duration,
        max_duration,
    ):
        self._clip_finder = clip_finder
        self._media_editor = media_editor
        self._logger = logger
        self._min_duration = min_duration
        self._max_duration = max_duration

    def trim_clips(self, transcription: Transcription, file_path: str) -> list[str]:
        clips = self._clip_finder.find_clips(transcription=transcription)
        clips = [
            clip
            for clip in clips
            if self._min_duration
            <= (clip.end_time - clip.start_time)
            <= self._max_duration
        ]
        self._logger.info(f"Found {len(clips)} clips")
        return self.__trim(clips, file_path)

    def __trim(self, clips: list[Clip], file_path: str):
        original_video_name = os.path.splitext(os.path.basename(file_path))[0]
        clips_folder = os.path.join(RESULTS_PATH, original_video_name)
        os.makedirs(clips_folder, exist_ok=True)

        media_file = AudioVideoFile(file_path)

        clip_paths = []

        for clip in clips:
            clip_name = (
                f"{format_time(clip.start_time, '_')}"
                f"__{format_time(clip.end_time, '_')}.mp4"
            )
            clip_path = os.path.join(clips_folder, clip_name)

            self._logger.info(
                f"Trimming clip {format_time(clip.start_time)}-{format_time(clip.end_time)}..."
            )

            self._media_editor.trim(
                media_file=media_file,
                start_time=clip.start_time,
                end_time=clip.end_time,
                trimmed_media_file_path=clip_path,
            )

            clip_paths.append(clip_path)

        return clip_paths
