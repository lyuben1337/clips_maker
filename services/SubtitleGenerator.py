import json
import os.path
import re

import whisper
from abstractions.ISubtitleGenerator import ISubtitleGenerator
from moviepy import VideoFileClip, CompositeVideoClip, TextClip
from moviepy.video.fx import CrossFadeIn, CrossFadeOut

from utils.Logger import Logger


class SubtitleGenerator(ISubtitleGenerator):
    def __init__(
        self,
        device: str,
        font_path: str,
        color: str,
        logger: Logger,
        max_words_per_line: int = None,
        stroke_color: str = None,
        stroke_width: int = None,
    ):
        self._max_words_per_line = max_words_per_line
        self._font_path = font_path
        self._color = color
        self._stroke_color = stroke_color
        self._stroke_width = stroke_width
        self._logger = logger
        self._device = device

    def add_subtitles(self, file_path: str, subtitles: list):
        video = VideoFileClip(file_path)

        self._logger.info(f"Detected {len(subtitles)} subtitles")
        self._logger.info(f"Adding subtitles to video with the following format:")
        self._logger.info(f"Font: {os.path.basename(self._font_path)}")
        self._logger.info(f"Color: {self._color}")
        if self._stroke_color:
            self._logger.info(f"Stroke color: {self._stroke_color}")
        if self._stroke_width:
            self._logger.info(f"Stroke width: {self._stroke_width}px")

        sub_clips = [
            self.__subtitle_generator(text, start, end, video.size)
            for (start, end), text in subtitles
        ]

        final_video = CompositeVideoClip([video] + sub_clips, size=video.size)

        temp_file_path = file_path.replace(".mp4", "_temp.mp4")
        final_video.write_videofile(
            filename=temp_file_path, codec="libx264", audio_codec="aac"
        )
        os.replace(temp_file_path, file_path)

        return subtitles

    def __subtitle_generator(self, txt: str, start: int, end: int, size):
        _, video_height = size
        fontsize = int(video_height * 0.0375)
        return (
            TextClip(
                text=txt,
                font=self._font_path,
                color=self._color,
                duration=end - start,
                stroke_color=self._stroke_color,
                stroke_width=self._stroke_width,
                method="caption",
                text_align="center",
                font_size=fontsize,
                size=size,
            )
            .with_effects([CrossFadeIn(0.1), CrossFadeOut(0.1)])
            .with_start(start)
            .with_end(end)
        )

    def generate_subtitles(self, file_path: str) -> list:
        model = whisper.load_model("turbo")

        self._logger.info("Using whisper model turbo")

        result = model.transcribe(
            file_path,
            word_timestamps=self._max_words_per_line is not None,
        )

        subtitles = []

        if not self._max_words_per_line:
            for segment in result["segments"]:
                start = segment["start"]
                end = segment["end"]
                text = re.sub(r"[^\w\s]", "", segment["text"])
                subtitles.append(((start, end), text))
            return subtitles

        self._logger.info(f"Max words per line: {self._max_words_per_line}")

        for segment in result["segments"]:
            words = segment.get("words", [])
            if not words:
                continue

            for i in range(0, len(words), self._max_words_per_line):
                word_chunk = words[i : i + self._max_words_per_line]
                start = word_chunk[0]["start"]
                end = word_chunk[-1]["end"]
                text = " ".join(
                    re.sub(r"[^\w\s]", "", word["word"]) for word in word_chunk
                )
                subtitles.append(((start, end), text))

        return subtitles

    def save_to_file(self, file_path: str, subtitles: list):
        try:
            with open(file_path, "x", encoding="utf-8") as file:
                json.dump(subtitles, file, indent=4, ensure_ascii=False)
            print(f"Subtitles successfully saved to {file_path}")
        except Exception as e:
            print(f"Error saving subtitles to file: {str(e)}")

    def load_from_file(self, file_path: str) -> list:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                subtitles = json.load(file)
            print(f"Subtitles successfully loaded from {file_path}")
            return subtitles
        except Exception as e:
            print(f"Error loading subtitles from file: {str(e)}")
