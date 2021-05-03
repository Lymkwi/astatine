"""Audio module template"""


class AudioModule:
    def __init__(self):
        raise NotImplementedError("Implement this")

    def process(self, sentence: str):
        raise NotImplementedError("Implement this")

    def give_configuration(self, config: dict):
        raise NotImplementedError("Implement this")