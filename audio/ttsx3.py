"""Audio module for the pyttsx3 audio library"""

# External partial imports
from pathlib import Path
from logging import getLogger
from random import randrange

# Internal partial imports
from .model import AudioModule

# Checked imports
try:
    import pyttsx3 as tts
except ModuleNotFoundError:
    # Cannot use pyttsx3
    pass

# Logging
logger = getLogger("astatine.audio.ttsx3")

# Module name
module = "TTSX3Module"

class TTSX3Module(AudioModule):
    def __init__(self):
        # Initialize the pyttsx3 audio engine
        self.engine = tts.init()
        logger.debug("Engine successfully initialised")
        self.save_path = None
    
    def give_configuration(self, config: dict):
        if "save_path" in config:
            # Verify the save path
            if not isinstance(config["save_path"], str):
                assert(False) # FIXME proper errors
            sp = Path(config["save_path"])
            if not sp.exists() or not sp.is_dir():
                assert(False) # FIXME
            
            # Get the string to that directory that is
            # - resolved (canonical path with no symlinks/detours)
            # - absolute (starts at the root of the current device)
            self.save_path = str(sp.resolve().absolute())
    
    def process(self, sentence: str):
        # Verify the variable type
        if not isinstance(sentence, str):
            assert(False) # FIXME

        # Create the audio from that sentence
        # The problem is that PyTTSX3 can only save to a file or say it
        # Ideally, we will use the layer of the application to say
        # the audio, so we need to save it, extract it, then return it
        random_id = randrange(2**12) # Random number
        save_path = Path("/tmp") / f"{random_id}.tmp"

        # Create the file for temporary saving
        logger.debug(f"Temporarily saving audio to {save_path}")
        try:
            save_path.touch()
        except PermissionError:
            logger.error(f"Permission denied to touch '{save_path}'")
            assert(False) # FIXME
        except Exception as e:
            logger.error(f"Unknown exception of type '{type(e)}' on path touch")
            assert(False) # FIXME
        else:
            logger.debug(f"Successfully touched '{save_path}'")
        
        # Save file
        self.engine.save_to_file(sentence, str(save_path))
        self.engine.runAndWait()

        # Hopefully we can read the file back
        try:
            data = open(str(save_path), "rb").read()
        except FileNotFoundError:
            logger.error(f"FileNotFound on {random_id}.tmp in temporary directory")
            assert(False) # FIXME
        except Exception as e:
            logger.error(f"Unknown exception 'f{e}' reading in temporary directory")
            assert(False) # FIXME
        else:
            logger.debug(f"Successfully retrieved temporary save in '{save_path}'")
        
        # Finally, remove the file
        try:
            save_path.unlink()
        except Exception as e:
            logger.error(f"Unkonwn exception of type '{type(e)}' when unlinking file")
            assert(False) # FIXME
        else:
            logger.debug(f"Successfully unlinked '{save_path}'")

        # And return the data when we are done
        return data