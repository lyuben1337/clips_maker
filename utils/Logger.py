import logging
import sys
import time

from rich.console import Console
from rich.live import Live
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text


class LoggerOutput:
    def __init__(self, logger_method):
        self.logger_method = logger_method

    def write(self, message):
        text = message.strip()
        if text:
            self.logger_method(text)

    def flush(self):
        pass


class Logger:
    def __init__(self):
        self.current_title = None
        self.current_subtitle = None
        self.current_stage = None
        self.title_start_time = None
        self.stage_start_time = None
        self.subtitle_start_time = None

        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

        self.console = Console(file=sys.stdout)

        self.logger = self._setup_logger()

        self.live = Live(console=self.console, refresh_per_second=10, auto_refresh=True)
        self.live.start()

        sys.stdout = LoggerOutput(self.debug)
        sys.stderr = LoggerOutput(self.debug)

    def set_level(self, level):
        self.logger.setLevel(level)

    def _setup_logger(self):
        logger = logging.getLogger("rich_logger")
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        handler = RichHandler(console=self.console, show_time=True, show_path=False)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

        return logger

    def log_progress(self, title: str = None, subtitle: str = None, stage: str = None):
        self._update_stage(stage)
        self._update_subtitle(subtitle)
        self._update_title(title)
        if title:
            self.info(f"{title}...")
        if subtitle:
            self.info(f"{subtitle}...")
        if stage:
            self.info(f"{stage}...")

        self._update_panel()

    def _update_stage(self, stage):
        if stage and stage != self.current_stage:
            self._log_elapsed_time(self.current_stage, self.stage_start_time)
            self.current_stage = stage
            self.stage_start_time = time.time()

    def _update_subtitle(self, subtitle):
        if subtitle and subtitle != self.current_subtitle:
            self._log_elapsed_time(self.current_subtitle, self.subtitle_start_time)
            self.current_subtitle = subtitle
            self.subtitle_start_time = time.time()

    def _update_title(self, title):
        if title and title != self.current_title:
            self._log_elapsed_time(self.current_title, self.title_start_time)
            self.current_title = title
            self.title_start_time = time.time()

    def _log_elapsed_time(self, task, start_time):
        if task and start_time:
            elapsed_time = time.time() - start_time
            self.info(f"'{task}' completed in {elapsed_time:.2f} seconds.")

    def _update_panel(self):
        stage = f"{self.current_stage}..." if self.current_stage else ""
        title = f"[bold magenta]{self.current_title}" if self.current_title else None
        subtitle = (
            f"[bold magenta]{self.current_subtitle}" if self.current_subtitle else None
        )
        stage_panel = Panel(
            Text(stage, justify="center", style="bold white on blue"),
            title=f"{title}",
            subtitle=subtitle,
            title_align="left",
        )
        self.live.update(stage_panel, refresh=True)

    def info(self, message: str):
        self.logger.info(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def error(self, message: str):
        self.logger.error(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def stop(self):
        self._log_elapsed_time(self.current_stage, self.stage_start_time)
        self._log_elapsed_time(self.current_subtitle, self.subtitle_start_time)
        self._log_elapsed_time(self.current_title, self.title_start_time)
        self.live.stop()

        # Restore original stdout and stderr
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
