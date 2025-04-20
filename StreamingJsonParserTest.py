import json

class StreamingJsonParserTest:
    def __init__(self):
        """
        Initializes the parser with an empty buffer and an empty parsed object.
        """
        self.buffer = ""
        self.cursor = 0