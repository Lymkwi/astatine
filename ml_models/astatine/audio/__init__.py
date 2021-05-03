"""Initialization of the audio modules"""

import logging
import importlib
from pathlib import Path

def init_logger():
    logger = logging.getLogger("astatine.audio")
    logger.debug("Audio logger initialized")

init_logger()

logger = logging.getLogger("astatine.audio")

known_modules = {}

def search_modules():
    """Search for all the modules defined in the Captioning module"""
    p = Path(__file__).parent
    for file in p.glob("*.py"):
        if file.name in ["model.py", "__init__.py"]:
            # Ignore those
            continue
        # Dynamically import
        modname = file.name[:-3]
        logger.debug(f"Peeking into python module '{modname}'")
        cursymbols = importlib.import_module(f"{__name__}.{modname}")
        if hasattr(cursymbols, "module"):
            module_name = cursymbols.module
            module_class = cursymbols.__getattribute__(module_name)
            # And now it's in the current symbols table at the root level
            known_modules[module_name] = module_class
            logger.debug(f"Loaded module '{module_name}' from python module '{modname}'")

search_modules()

def load_module(name: str):
    # FIXME do all the types assert
    # FIXME check that this is not, in fact, monstrously dangerous
    if not name in known_modules:
        assert(False)
    return known_modules[name]()
