from typing import Union, List
from io import IOBase

class Fpos:
    """Windowed view of an input stream"""
    def __init__(self, data : Union[str, IOBase, List[str]]):
        """ - Provides a windowed view of an input stream.  Each line is assumed to be terminated by a newline.
        Args:
        data :Union[str, IOBase, List[str]]: A file path or derivative class of IOBase to read from, or a list of lines
        """
        if type(data) is str:
            with open(data, "rt") as f:
                lines = f.readlines()
        elif isinstance(data, IOBase):
            lines = data.readlines()
        elif type(data) is list:
            lines = data
        else:
            raise ValueError("Invalid data")
        self.lines = lines
        self.cpos = 0
        self.rpos = 0

    @property
    def v(self):
        """- Returns the current row and column view of the stream"""
        #print(self.rpos,self.cpos,self.lines[self.rpos][self.cpos:])
        return self.lines[self.rpos][self.cpos:]

    @property
    def eof(self):
        """- Returns true if the row is past the end of the stream"""
        if self.rpos >= len(self.lines):
            return True
        return False

    def skip(self, n):
        """- Moves the cursor forward
        Args:
            n :int: count of characters to move forward.  If the column moves
            past the end of line the row will be advanced and the column is set
            to 0
        """
        self.cpos += n
        if self.cpos >= len(self.lines[self.rpos]):
            self.cpos = 0
            self.rpos += 1