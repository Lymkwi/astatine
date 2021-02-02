#!/usr/bin/python3
#
# Practical Study
#
# Main structure : the chain is separated into two modules : captioning and TTS
# All of them have a model object defined in `model.py` that all implementations
# derive from. This file imports modules as configured (so far they're hard coded)
# and executes them on the image path given to it, placing the resulting sound
# file in a location known by both the application and this file (NIY).

"""Main module for image analysis"""

# External full imports
import logging
# External partial imports
from sys import argv # To retrieve the images
from pathlib import Path

# Internal full imports (to activate __init__ code)
import utils    # utils first to intialize logging
import audio
import captioning
# Internal partial import
from utils.config import configuration, save_configuration
from audio.ttsx3 import TTSX3Module
from captioning.dummy import DummyCaptionModule


# Logging
logger = logging.getLogger("astatine.main")

def main(img_path):
    """This is the main function, the entry point of the app"""
    logger.debug(f"Beginning process chain on '{img_path}'")

    # Image verification
    logger.debug("Verifying image authenticity")
    img_path = Path(img_path)
    if not img_path.exists():
        logger.error(f"Image '{img_path}' does not exist.")
        return # FIXME add errors
    else:
        logger.debug(f"Image '{img_path}' exits. \u2713")

    # Machine learning processing
    logger.debug("Obtaining image description")
    logger.debug("Initializing captioning module")
    captioning_module = captioning.load_module(configuration["captioning"]["module"])
    # process
    caption = captioning_module.process(img_path)

    # TTS
    logger.debug("Initializing TTS module")
    module = audio.load_module(configuration["audio"]["module"])
    result = module.process(caption)
    return result

if __name__ == "__main__":
    # Obtain images
    for img_path in argv[1:]:
        _ = main(img_path)
    # Save the configuration before leaving
    save_configuration(configuration)