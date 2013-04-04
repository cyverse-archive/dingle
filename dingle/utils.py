"""Utility methods for Dingle"""

import sys

def err_exit(error_msg):
    """Prints off an error message to stderr and exits."""
    sys.stderr.write(error_msg + "\n")
    sys.exit(-1)