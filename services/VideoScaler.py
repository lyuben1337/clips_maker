import os
import shutil
import subprocess

import cv2
import torch
from moviepy import VideoFileClip
from realesrgan import RealESRGANer

from abstractions.IVideoScaler import IVideoScaler
from utils.Logger import Logger
from utils.utils import RESULTS_PATH
from basicsr.archs.rrdbnet_arch import RRDBNet


class VideoScaler(IVideoScaler):
    def __init__(
        self,
        logger: Logger,
        target_width: int = 1080,
        ai: bool = True,
    ):
        self.target_width = target_width
        self.ai = ai
        self.logger = logger

        if ai:
            model = RRDBNet(
                num_in_ch=3,
                num_out_ch=3,
                num_feat=64,
                num_block=23,
                num_grow_ch=32,
                scale=4,
            )
            netscale = 4
            model_url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"

            self.scaler = RealESRGANer(
                scale=netscale,
                model_path=model_url,
                model=model,
                device=torch.device("mps"),
            )

    @staticmethod
    def __resize_video_with_moviepy(input_path, output_path, target_width):
        clip = VideoFileClip(input_path)
        aspect_ratio = clip.h / clip.w
        new_height = int(target_width * aspect_ratio)
        resized_clip = clip.resized(width=target_width)
        resized_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        return new_height

    def __process_frames_with_ai(self, file_path, temp_dir):
        frame_width, frame_height, fps = self.__extract_frames(file_path, temp_dir)
        frame_files = sorted(os.listdir(temp_dir))
        for i, frame_file in enumerate(frame_files, start=1):
            self.logger.info(f"Upscaling frame ({i}/{len(frame_files)})")
            frame_path = os.path.join(temp_dir, frame_file)
            frame = cv2.imread(frame_path, cv2.IMREAD_COLOR)
            upscaled_frame, _ = self.scaler.enhance(frame)
            _, resized_frame = self.__resize_frame(
                upscaled_frame, self.target_width, frame.shape[1], frame.shape[0]
            )
            cv2.imwrite(frame_path, upscaled_frame)

        return frame_width, frame_height, fps

    def scale(self, file_path):
        temp_output_path = file_path.replace(".mp4", "_scaled.mp4")

        if not self.ai:
            self.logger.info("Using MoviePy for resizing.")
            new_height = self.__resize_video_with_moviepy(
                file_path, temp_output_path, self.target_width
            )
        else:
            self.logger.info("Using AI for upscaling.")
            temp_dir = os.path.join(RESULTS_PATH, "temp_frames")
            os.makedirs(temp_dir, exist_ok=True)
            try:
                frame_width, frame_height, fps = self.__process_frames_with_ai(
                    file_path, temp_dir
                )
                self.__assemble_video(temp_dir, temp_output_path, fps, file_path)
                new_height = int(self.target_width * (frame_height / frame_width))
            finally:
                shutil.rmtree(temp_dir)

        self.logger.info(
            f"Video scaled to resolution: {self.target_width}x{new_height}"
        )
        os.replace(temp_output_path, file_path)

    @staticmethod
    def __extract_frames(file_path, temp_dir):
        cap = cv2.VideoCapture(file_path)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        frame_index = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_path = os.path.join(temp_dir, f"frame_{frame_index:04d}.png")
            cv2.imwrite(frame_path, frame)
            frame_index += 1

        cap.release()
        return frame_width, frame_height, fps

    @staticmethod
    def __resize_frame(frame, target_width, original_width, original_height):
        new_height = int(original_height * (target_width / original_width))
        return new_height, cv2.resize(
            frame, (target_width, new_height), interpolation=cv2.INTER_LANCZOS4
        )

    @staticmethod
    def __assemble_video(temp_dir, output_video_path, fps, original_video_path):
        temp_audio_path = os.path.join(temp_dir, "audio.aac")

        # Extract audio from the original video
        extract_audio_command = [
            "ffmpeg",
            "-y",
            "-i",
            original_video_path,
            "-vn",  # No video
            "-c:a",
            "copy",  # Copy audio without re-encoding
            temp_audio_path,
        ]
        subprocess.run(
            extract_audio_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Assemble video with audio
        assemble_command = [
            "ffmpeg",
            "-y",
            "-framerate",
            str(fps),
            "-i",
            f"{temp_dir}/frame_%04d.png",
            "-i",
            temp_audio_path,
            "-c:v",
            "libx264",  # Encode video
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "copy",  # Copy original audio parameters
            "-shortest",  # Ensures video and audio durations match
            output_video_path,
        ]
        subprocess.run(
            assemble_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
