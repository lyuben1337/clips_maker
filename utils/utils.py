import os
import sys

from dotenv import load_dotenv

load_dotenv()


def format_time(seconds, delimiter=":"):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{int(hours):02}{delimiter}{int(minutes):02}{delimiter}{int(secs):02}"


def get_base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


BASE_PATH = get_base_path()
RESOURCES_PATH = os.path.join(BASE_PATH, "resources")

SOURCES_PATH = os.path.join(RESOURCES_PATH, "sources")
RESULTS_PATH = os.path.join(RESOURCES_PATH, "results")
ASSERTS_PATH = os.path.join(RESOURCES_PATH, "asserts")

PYANNOTE_TOKEN = os.getenv("PYANNOTE_TOKEN")
