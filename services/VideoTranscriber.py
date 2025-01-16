import torch
import whisperx
from clipsai import Transcriber, Transcription
from clipsai.transcribe.transcriber import TranscriberConfigManager
from clipsai.utils.pytorch import get_compute_device, assert_valid_torch_device
from clipsai.utils.type_checker import TypeChecker

from abstractions.IVideoTranscriber import IVideoTranscriber
from utils.Logger import Logger


class CustomTranscriberConfigManager(TranscriberConfigManager):
    def get_valid_languages(self) -> list[str]:
        return super().get_valid_languages() + ["ru"]

    def get_valid_model_sizes(self) -> list[str]:
        return super().get_valid_model_sizes() + ["turbo"]


class VideoTranscriber(Transcriber, IVideoTranscriber):
    def __init__(
        self,
        logger: Logger,
        model_size: str = None,
        device: str = None,
        precision: str = None,
    ) -> None:
        self._logger = logger
        self._config_manager = CustomTranscriberConfigManager()
        self._type_checker = TypeChecker()

        if device is None:
            device = get_compute_device()
        if precision is None:
            precision = "float16" if torch.cuda.is_available() else "int8"
        if model_size is None:
            model_size = "large-v2" if torch.cuda.is_available() else "tiny"

        # assert_valid_torch_device(device)
        self._config_manager.assert_valid_model_size(model_size)
        self._config_manager.assert_valid_precision(precision)

        self._logger.info(f"Using device: {device}")
        self._logger.info(f"Using model: {model_size}")

        self._precision = precision
        self._device = device
        self._model_size = model_size
        self._model = whisperx.load_model(
            whisper_arch=self._model_size,
            device=self._device,
            compute_type=self._precision,
        )

    def transcribe(
        self,
        audio_file_path: str,
        iso6391_lang_code: str or None = None,
        batch_size: int = 16,
    ) -> Transcription:
        if not iso6391_lang_code:
            self._logger.info("Language not specified, using auto-detection:")
        transcription = super().transcribe(
            audio_file_path, iso6391_lang_code, batch_size
        )
        self._logger.info(f"Language: {transcription.language}")
        self._logger.info(f"Founded {len(transcription.words)} sentences")
        return transcription
