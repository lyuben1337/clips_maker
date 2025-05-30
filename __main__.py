from utils.Logger import Logger

logger = Logger()
logger.set_level("DEBUG")

import os
import types
import sys

from torchvision.transforms.functional import rgb_to_grayscale

functional_tensor = types.ModuleType("torchvision.transforms.functional_tensor")
functional_tensor.rgb_to_grayscale = rgb_to_grayscale
sys.modules["torchvision.transforms.functional_tensor"] = functional_tensor

from clipsai import MediaEditor, ClipFinder
from services.BackgroundGenerator import BackgroundGenerator
from services.SubtitleGenerator import SubtitleGenerator
from services.VideoPipeline import VideoPipeline
from services.VideoResizer import VideoResizer
from services.VideoTranscriber import VideoTranscriber
from services.VideoTrimmer import VideoTrimmer
from utils.utils import SOURCES_PATH, ASSERTS_PATH
from services.VideoScaler import VideoScaler
from services.FrameRateReducer import FrameRateReducer
from services.PauseRemover import PauseRemover


if __name__ == "__main__":
    media_editor = MediaEditor()
    clip_finder = ClipFinder(device="mps")

    frame_rate_reducer = FrameRateReducer(target_fps=24, logger=logger)
    video_transcriber = VideoTranscriber(
        model_size="turbo", logger=logger, device="cpu"
    )
    video_trimmer = VideoTrimmer(
        media_editor=media_editor,
        clip_finder=clip_finder,
        min_duration=40,
        max_duration=120,
        logger=logger,
    )
    video_resizer = VideoResizer(
        media_editor=media_editor,
        logger=logger,
        face_margin=300,
        aspect_ratio=(3, 4),
        device="cpu",
    )
    video_scaler = VideoScaler(target_width=1080, ai=False, logger=logger)
    background_generator = BackgroundGenerator(target_ratio=(9, 16), logger=logger)
    subtitle_generator = SubtitleGenerator(
        device="cpu",
        font_path=os.path.join(ASSERTS_PATH, "DelaGothicOne-Regular.ttf"),
        color="white",
        max_words_per_line=2,
        stroke_width=2,
        stroke_color="black",
        logger=logger,
    )
    pause_remover = PauseRemover(
        buffer_time=0.2,
        logger=logger,
    )

    pipeline = VideoPipeline(
        frame_rate_reducer=frame_rate_reducer,
        video_transcriber=video_transcriber,
        video_trimmer=video_trimmer,
        video_scaler=video_scaler,
        video_resizer=video_resizer,
        background_generator=background_generator,
        subtitle_generator=subtitle_generator,
        pause_remover=pause_remover,
        logger=logger,
    )
    #
    # files_to_process = [
    #     file for file in sorted(os.listdir(SOURCES_PATH)) if file.endswith(".mp4")
    # ]
    # for i, file in enumerate(files_to_process, start=1):
    #     file_path = os.path.join(SOURCES_PATH, file)
    #     logger.log_progress(
    #         title=f"Processing video {file} ({i}/{len(files_to_process)})"
    #     )
    # pipeline.process_video(
    #     "/Users/lyuben1337/Projects/clips_maker/resources/sources/s01e05_480.mp4"
    # )

    test_file = "/Users/lyuben1337/Desktop/clips/202501212230 (4).mp4"
    frame_rate_reducer.reduce(test_file)
    video_resizer.resize(test_file)
    video_scaler.scale(test_file)
    background_generator.add_background(test_file)
    subtitles = subtitle_generator.generate_subtitles(test_file)
    subtitle_generator.add_subtitles(test_file, subtitles)
    pause_remover.remove_pauses(test_file, subtitles)

    logger.stop()
