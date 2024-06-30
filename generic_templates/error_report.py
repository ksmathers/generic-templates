from enum import Enum
import sys

class ErrorLevel(Enum):
    INFO=0
    WARN=1
    ERROR=2

class ErrorReport:
    Level = ErrorLevel

    def __init__(self):
        self.errors = []
        self.max_level : ErrorLevel = ErrorLevel.INFO

    def warn(self, msg):
        self.show(ErrorLevel.WARN, msg)

    def info(self, msg):
        self.show(ErrorLevel.INFO, msg)

    def error(self, msg):
        self.show(ErrorLevel.ERROR, msg)

    def show(self, level : ErrorLevel, msg):
        self.errors.append(msg)
        if self.max_level.value < level.value: self.max_level = level
        print(f"{level.name}: {msg}", file=sys.stderr)

    def exit_on_error(self):
        if self.max_level.value > ErrorLevel.WARN.value:
            print("Exiting on error")
            sys.exit(1)

    def test(self, condition, msg, level : ErrorLevel = ErrorLevel.ERROR):
        if not condition:
            self.show(level, msg) 

    def to_string(self):
        return "\n".join(self.errors)
    
