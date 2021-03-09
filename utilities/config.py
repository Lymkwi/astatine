"""Configuration manipulation"""

# External full import
import yaml
import logging
# External partial import
from pathlib import Path

def default_configuration():
    return {
        'audio': {
            'module': 'TTSX3Module',
        },
        'captioning': {
            'module': 'DummyCaptionModule'
        },
        'logging': {
            'levels': {
                'astatine': 'DEBUG',
                'astatine.audio': 'DEBUG',
                'astatine.caps': 'DEBUG',
                'astatine.utils': 'DEBUG'
            },
        }
    }

def get_config(path="config.cfg"):
    # Try and open the configuration
    config_path = Path(path)
    if not config_path.exists():
        # Load default save as backup
        return default_configuration()

    # Add checks (FIXME)
    config = yaml.safe_load(open(path, "r"))
    return config

configuration = get_config()

def save_configuration(conf, path="config.cfg"):
    config_path = Path(path)
    # Check that we can write
    try:
        config_path.touch()
        fp = open(path, "w")
    except:
        assert(False) # Add logging if you want
    
    # FIXME add security
    yaml.dump(conf, fp)
