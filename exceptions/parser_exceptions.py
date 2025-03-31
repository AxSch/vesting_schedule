from typing import Optional


class CSVParserError(Exception):
    def __init__(self, message, line_number: Optional[int] = None):
       if line_number:
           message = f"{message} (line {line_number})"
       super().__init__(message)
