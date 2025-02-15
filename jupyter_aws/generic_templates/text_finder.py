import os
import re

class TextFinder:
    """
    Text parsing tool with streaming invocation API

    Example:
       tf = TextFinder("this is a **secret** message")
       secret = tf.find("**").after().mark().find("**").copy()

    Mark sets a start position, copy() returns the string between
    the mark and the current cursor position.
    """
    def __init__(self, s: str):
        self.s = s
        self.lpos = 0
        self.pos = 0
        self.lneedle = ""
    
    def find(self, needle = None):
        """
        Positions the cursor at the first character of the 
        given string.   
        """
        if needle is None: needle = self.lneedle
        npos = self.s.index(needle, self.pos)
        if npos < 0:
            raise ValueError(f"text {needle} not found")
        self.pos = npos
        self.lneedle = needle
        return self
    
    def findx(self, pattern, limit=None):
        """
        Positions the cursor at the first character of the
        given regular expression.
        """
        npos = self.locatex(pattern)
        if limit is not None and npos > limit:
            raise ValueError(f"pattern {pattern} not found before {limit}")
        if npos < 0:
            raise ValueError(f"pattern {pattern} not found")
        self.pos = npos
        return self
    
    
    def rfind(self, needle = None):
        """
        Positions the cursor at first character of the last
        occurance of the given string 'needle' searching backward 
        from the current cursor position, (or from the end of the string if 
        the cursor position is 0)
        """
        if needle is None: needle = self.lneedle
        self.pos = self.s.rindex(needle, self.lpos, self.pos-1)
        self.lneedle = needle
        return self
    
    def after(self, needle = None):
        """
        Positions the cursor after the last search key, or after 
        text supplied in the 'needle' parameter.

        Raise ValueError if the start of the string doesn't match needle.
        """
        if needle is None: needle = self.lneedle
        if not self.s[self.pos:].startswith(needle):
            raise ValueError(f"string {needle} not found at start of string")
        self.pos += len(self.lneedle)
        self.lneedle = needle
        return self
    
    def trim(self):
        """
        Skips the cursor past white space including newlines.
        """
        while self.s[self.pos] in " \n\t": self.pos+=1
        return self
    
    def rtrim(self):
        """
        Skips the cursor left past white space including newlines
        """
        self.pos-=1
        while self.s[self.pos]==' ' or self.s[self.pos]=='\n': self.pos-=1
        self.pos+=1
        return self
    
    def skip(self, n:int):
        """
        Skips a fixed number of characters to the right
        """
        self.pos += n
        return self
    
    def locatex(self, find_regex:str):
        """
        Returns the location of a regex with search starting from the current cursor position
        """
        match = re.search(find_regex, self.s[self.pos:])
        if match is not None:
            s,e = match.span()
            self.lneedle = self.s[self.pos+s:self.pos+e]
            #print("lneedle <=", self.lneedle)
            return self.pos + s
        return -1
    
    def spanx(self, allowed_regex:str):
        """
        Skips past a group of characters starting from the cursor where the group of characters
        is represented by a regular expression
        """
        match = re.match(allowed_regex, self.s[self.pos:])
        if match is not None:
            #print(match)
            self.pos += match.span()[1]
        return self

    def dequote(self):
        """
        Simple remove matching quotes around a marked string region moving the lpos and the cpos 
        toward one another if matching boundary markers are found at both ends of the string.  Any
        character at the start of the marked region is compared to the last character, and if they 
        match they are both removed from the selected lpos:pos region.
        """
        startquote = self.s[self.lpos]
        if self.s[self.pos-1] == startquote:
            self.lpos+=1
            self.pos-=1
        return self
    
    def dequotex(self, startx:str, endx:str):
        """
        Finds and extracts the startx and endx delimited middle of a string where startx and endx are regular 
        expressions.   Searching is done forward of the current cursor position for the start marker, and then 
        forward from there for the end marker.   The mark and pos after calling dequotex will be inside the
        start and end locations.
        """
        self.findx(startx).after().mark().findx(endx)
        return self
        
    def span(self, allowed:str):
        """
        Skips past a group of characters starting from the cursor where the group of characters
        is listed in the 'allowed' parameter
        """
        while self.s[self.pos] in allowed:
            self.pos += 1
        return self
    
    def copy(self):
        """
        Returns the string between the mark and the current cursor position, or the full string up
        to the current cursor position if the mark has not been set.
        """
        return self.s[self.lpos:self.pos]
        
    def end(self):
        """
        Moves the cursor to the end of the string
        """
        self.pos = len(self.s)
        return self
    
    def mark(self):
        """
        Sets the mark for the left side of the string capture
        """
        self.lpos = self.pos
        return self