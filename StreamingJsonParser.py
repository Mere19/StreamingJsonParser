import json

"""
Assumptions:
- The input is a valid JSON object.
- The JSON string can be parsed into a (nested) Python dictionary.
- The get() method returns the current state of the current root JSON object.
"""

"""
- Key is closed when the corresponding value is set (doesn't have to be completed).
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
            self.cursor += 1
            if char == '{':
                self._open_object()
            elif char == '}':
                self._close_object()
            elif char == '"':
                # handle strings
                s = self.buffer[self.cursor:self.buffer.find('"', self.cursor)]
                self.cursor += len(s)
                self._handle_strings(s)
            elif char in '0123456789':
                # handle numbers
                number = self.buffer[self.cursor:self.buffer.find(',', self.cursor)]
                self.cursor += len(number)
                self._handle_numbers(float(number))
            elif char in 'tf':
                # handle boolean values
                boolean = self.buffer[self.cursor:self.buffer.find(',', self.cursor)]
                self.cursor += len(boolean)
                self._handle_boolean(boolean == 'true')
            elif char == '[':
                self._open_list()
            elif char == ']':   
                self._close_list()
            elif char in ' \n\t\r:,':
                pass
            else:
                # TODO: handle other characters
                pass

            self.cursor += 1

    def _open_object(self):
        """
        Creates a new object to be used for parsing.
        """
        new_object = {}
        if self.current_object is None:
            self.parsed_object = new_object
        else:
            self.current_object[self.current_key] = new_object
            self.stack.append(self.current_object)
        
        self.current_object = new_object
        self.current_key = None
    
    def _close_object(self):
        """
        Completes the current object and resets the buffer.
        """
        if self.stack:
            # If stack is not empty, continue parsing the parent object
            parent_object = self.object_stack.pop()
            self.current_object = parent_object
        else:
            # If stack is empty, we are done parsing
            self.current_object = None

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
        # if number is an element of a list, append it to the list
        if self.current_list is not None:
            self.current_list.append(number)
        # if number is a value, set it as the current value
        elif self.current_key is not None:
            self.current_object[self.current_key] = number
            self.current_key = None
        else:
            raise Exception("Invalid state: Cannot parse number without a list or a key")

    def _handle_strings(self, s):
        """
        Handles strings in the JSON object.
        """        
        # if s is an element of a list, append it to the list
        if self.current_list is not None:
            self.current_list.append(s)
        # if s is a key, set it as the current key
        elif self.current_key is None:
            self.current_key = s
        # if s is a value, set it as the current value
        elif self.current_key is not None:
            self.current_object[self.current_key] = s
            self.current_key = None
        else:
            raise Exception("Invalid state: Cannot parse string without a list or an object")

    def _handle_boolean(self, boolean):
        """
        Handles boolean values in the JSON object.
        """
        if self.current_list is not None:
            self.current_list.append(boolean)
        elif self.current_key is not None:
            self.current_object[self.current_key] = boolean
            self.current_key = None
        else:
            raise Exception("Invalid state: Cannot parse boolean without a list or a key")

    def _handle_null(self):
        """
        Handles null values in the JSON object.
        """
        if self.key is not None:
            self.current_object[self.key] = None
            self.key = None
        else:
            self.current_object = None