"""Initialization of the Astatine utilities"""

from .config import configuration
from .log import logger_levels_config, init_logger
logger_levels_config(configuration)
init_logger()
