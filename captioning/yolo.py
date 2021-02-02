"""Image captioning module with YOLO"""

import logging

# Internal partial import
from .model import CaptionModule

logger = logging.getLogger("astatine.caps.yolo")

module = "YOLOModule"

class YOLOModule(CaptionModule):
    def __init__(self):
        logger.debug("Initializing")