"""Initialization of the captioning modules"""

import logging

def init_logger():
    logger = logging.getLogger("astatine.caps")
    logger.debug("Captioning logger initialized")

init_logger()

from .dummy import DummyCaptionModule
from .yolo import YOLOModule

known_modules = ["DummyCaptionModule", "YOLOModule"]

def load_module(name: str):
    # FIXME do all the types assert
    # FIXME check that this is not, in fact, monstrously dangerous
    if not name in known_modules:
        assert(False)
    return eval(f"{name}()")