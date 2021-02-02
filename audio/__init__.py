"""Initialization of the audio modules"""

import logging
from pathlib import Path

def init_logger():
    logger = logging.getLogger("astatine.audio")
    logger.debug("Audio logger initialized")

init_logger()

from .ttsx3 import TTSX3Module

known_modules = ["TTSX3Module"]

def load_module(name: str):
    # FIXME do all the types assert
    # FIXME check that this is not, in fact, monstrously dangerous
    if not name in known_modules:
        assert(False)
    return eval(f"{name}()")
