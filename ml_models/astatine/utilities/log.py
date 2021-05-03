"""Logging utility"""

# External import
import logging

def init_logger():
    """Initialize the general logger."""
    # Configure the logger
    logger = logging.getLogger("astatine")

    # Creates a handler for proper formatting
    # it takes any message that arrives to the main Astatine logger
    # and formats them
    # FIXME this is all hardcoded
    globalfilehandler = logging.FileHandler("astatine.log")
    globalstreamhandler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s][%(name)-20s][%(levelname)-8s]"
        +"(%(filename)s::%(funcName)s::%(lineno)s) %(message)s")
    globalstreamhandler.setFormatter(formatter)
    globalfilehandler.setFormatter(formatter)
    logger.addHandler(globalfilehandler)
    logger.addHandler(globalstreamhandler)

    logger.debug("Initialized logger")

def logger_levels_config(conf: dict):
    """Set all of the logging levels as defined in the configuration dictionary provided.
    Said dictionary should have an entry at `d["logging"]["levels"]` which is a dictionary
    where the keys are the logger names and the value is anything that can go in
    `logging.Logger.setLevel`."""
    if conf["logging"] and conf["logging"]["levels"]:
        levels = conf["logging"]["levels"]
        for key in levels:
            # FIXME checks for types and error handling
            logger = logging.getLogger(key)
            logger.setLevel(levels[key])
