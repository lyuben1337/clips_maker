import os
import traceback

from abstractions.IBackgroundGenerator import IBackgroundGenerator
from abstractions.IFrameRateReducer import IFrameRateReducer
from abstractions.IPauseRemover import IPauseRemover
from abstractions.ISubtitleGenerator import ISubtitleGenerator
from abstractions.IVideoResizer import IVideoResizer
from abstractions.IVideoScaler import IVideoScaler
from abstractions.IVideoTranscriber import IVideoTranscriber
from abstractions.IVideoTrimmer import IVideoTrimmer
from utils.Logger import Logger


class VideoPipeline:
    def __init__(
        self,
        frame_rate_reducer: IFrameRateReducer,
        video_transcriber: IVideoTranscriber,
        video_trimmer: IVideoTrimmer,
        video_resizer: IVideoResizer,
        video_scaler: IVideoScaler,
        background_generator: IBackgroundGenerator,
        subtitle_generator: ISubtitleGenerator,
        pause_remover: IPauseRemover,
        logger: Logger,
    ):
        self._frame_rate_reducer = frame_rate_reducer
        self._video_transcriber = video_transcriber
        self._video_trimmer = video_trimmer
        self._video_resizer = video_resizer
        self._video_scaler = video_scaler
        self._background_generator = background_generator
        self._subtitle_generator = subtitle_generator
        self._pause_remover = pause_remover
        self._logger = logger

    def process_video(self, file_path: str) -> None:
        try:
            self._logger.log_progress(stage=f"Reducing frame rate")
            self._frame_rate_reducer.reduce(file_path)

            self._logger.log_progress(stage=f"Transcribing")
            transcription = self._video_transcriber.transcribe(
                file_path, iso6391_lang_code="ru"
            )

            self._logger.log_progress(stage=f"Trimming into clips")
            clips = self._video_trimmer.trim_clips(transcription, file_path)
            for i, clip in enumerate(clips, start=1):
                try:
                    self._logger.log_progress(
                        subtitle=f"Processing clip ({i}/{len(clips)}) {os.path.basename(clip)}",
                        stage=f"Resizing",
                    )
                    self._video_resizer.resize(clip)

                    self._logger.log_progress(stage=f"Scaling")
                    self._video_scaler.scale(clip)

                    self._logger.log_progress(stage=f"Generating background")
                    self._background_generator.add_background(clip)

                    self._logger.log_progress(stage=f"Generating subtitles")
                    subtitles = self._subtitle_generator.add_subtitles(clip)

                    self._logger.log_progress(stage=f"Removing pauses")
                    self._pause_remover.remove_pauses(clip, subtitles)
                except Exception as e:
                    self._logger.error(f"Clip {clip} processing failed: {str(e)}")
        except Exception as e:
            self._logger.error(f"Video processing pipeline failed: {str(e)}")
