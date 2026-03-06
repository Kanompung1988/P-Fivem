"""
Runtime handler registry for cross-module access (e.g. admin broadcast).
"""

from typing import Optional


line_handler = None
facebook_handler = None


def set_handlers(line=None, facebook=None):
    global line_handler, facebook_handler
    line_handler = line
    facebook_handler = facebook


def get_line_handler() -> Optional[object]:
    return line_handler


def get_facebook_handler() -> Optional[object]:
    return facebook_handler
