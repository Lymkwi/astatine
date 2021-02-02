"""Dummy image captioning"""

# External full import
import logging
# External partial import
from pathlib import Path

# Internal partial import
from .model import CaptionModule

# Logging
logger = logging.getLogger("astatine.caps.dummy")

class DummyCaptionModule(CaptionModule):
    def __init__(self):
        logger.debug("Initialized dummy captioning module")

    def process(self, img_path: Path):
        logger.debug(f"Processing {img_path}")
        return "I don't know."