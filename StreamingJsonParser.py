import json

"""
Assumptions:
- The input is a valid JSON string.
- The JSON string can be parsed into a (nested) Python dictionary.
- The get() method returns the current state of the current root JSON object.
"""

"""
- Key is closed when the corresponding value is set.
"""

# TODO: rephrase the 
# TODO: create exception types

class StreamingJsonParser:
    def __init__(self):
        """
        Initializes the parser with an empty buffer and an empty parsed object.
        """
        self.buffer = ""
        self.cursor = 0  # Tracks the position of the next char to be parsed in buffer
        self.object_stack = []  # Tracks the stack of objects being parsed
        self.current_object = None  # Tracks the current object being constructed
        self.current_key = None  # Tracks the current key being processed
        self.list_stack = [] # Tracks the stack of lists being parsed
        self.current_list = None  # Tracks the current list being constructed
        self.parsed_object = None   # TODO: this should be the root object

    def consume(self, buffer: str):
        """
        Consumes a chunk of JSON data and updates the internal buffer.
        """
        self.buffer += buffer
        self._parse_buffer()

    def get(self):
        """
        Returns the current state of the parsed JSON object.
        TODO: this should be the root object
        """
        return self.parsed_object

    def _parse_buffer(self):
        """
        Attempts to parse the current buffer incrementally.
        Updates the parsed_object with the latest valid JSON state.
        """
        while self.cursor < len(self.buffer):
            char = self.buffer[self.cursor]
            if char == '{':
                self._open_object()
            elif char == '}':
                self._close_object()
            elif char == '"':
                # handle string (key or value)
                if self.key is None:
                    self._handle_key()
                else:
                    self._handle_values()
            elif char == ':':
                self.key = None
            elif char in ' \n\t\r':
                pass
            elif char == '[':
                self._open_list()
            elif char == ']':   
                # handle end of list
                if self.stack:
                    parent_object, parent_key = self.stack.pop()
                    if isinstance(parent_object, list):
                        parent_object.append(self.current_object)
                    else:
                        parent_object[parent_key] = self.current_object
                    self.current_object = parent_object
                else:
                    self.parsed_object = self.current_object
                    self.current_object = None
            else:
                # TODO: handle other characters
                pass

            self.cursor += 1

    def _open_object(self):
        """
        Creates a new object to be used for parsing.
        """
        if self.current_object is not None:
            self.stack.append((self.current_object, self.curr_key))
        self.current_object = {}
        self.curr_key = None
    
    def _close_object(self):
        """
        TODO: Completes the current object and resets the buffer.
        """
        if self.stack:
            parent_object, parent_key = self.stack.pop()
            if parent_key is not None:
                parent_object[parent_key] = self.current_object
            else:
                self.parsed_object = self.current_object
            self.current_object = parent_object
        else:
            # If stack is empty, we are done parsing
            self.parsed_object = self.current_object
            self.current_object = None
        self.key = None

    def _open_list(self):
        """
        Creates a new list to be used for parsing.
        """
        new_list = []
        if self.current_key is not None:
            self.current_object[self.key] = new_list
            self.key = None
            self.list_stack.append(new_list)
        elif self.current_list is not None:
            self.current_list.append(new_list)
            self.list_stack.append(self.current_list)
        else:
            raise Exception("Invalid state: Cannot open list without a key or current list")
        
        self.current_list = new_list

    def _close_list(self):
        """
        Completes the current list and resets the buffer.
        """
        if self.current_list is not None:
            if self.list_stack:
                self.current_list = self.list_stack.pop()
            else:
                self.current_list = None
        else:
            raise Exception("Invalid state: No open list to be closed")

    def _handle_key(self, key):
        """
        Handles the key in the JSON object.
        """
        if self.key is None:
            self.key = key

    def _handle_lists(self, value):
        """
        TODO: Handles the lists in the JSON object.
        """
        if isinstance(value, list):
            self.current_object[self.key] = value
            self.key = None
        elif isinstance(value, dict):
            self.current_object[self.key] = value
            self.key = None
        else:
            raise Exception("Invalid value for list")

    def _handle_values(self, value):
        """
        Handles the values in the JSON object.
        """
        if isinstance(value, dict):
            self.current_object[self.key] = value
            self.key = None
        elif isinstance(value, list):
            self.current_object[self.key] = value
            self.key = None
        elif isinstance(value, (int, float)):
            self._handle_numbers(value)
        elif isinstance(value, str):
            self._handle_strings(value)
        elif isinstance(value, bool):
            self._handle_boolean(value)
        elif value is None:
            self._handle_null()

    def _handle_numbers(self, number):
        """
        Handles numbers in the JSON object.
        """
        if self.key is not None:
            self.current_object[self.key] = number
            self.key = None

    def _handle_strings(self, string):
        """
        Handles strings in the JSON object.
        """
        if self.key is not None:
            self.current_object[self.key] = string
            self.key = None
        else:
            self.current_object = string

    def _handle_boolean(self, boolean):
        """
        Handles boolean values in the JSON object.
        """
        if self.key is not None:
            self.current_object[self.key] = boolean
            self.key = None
        else:
            self.current_object = boolean

    def _handle_null(self):
        """
        Handles null values in the JSON object.
        """
        if self.key is not None:
            self.current_object[self.key] = None
            self.key = None
        else:
            self.current_object = None