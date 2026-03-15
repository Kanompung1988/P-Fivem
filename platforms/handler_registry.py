"""
Runtime handler registry for cross-module access (e.g. admin broadcast).
"""

from typing import Optional


line_handler = None
facebook_handler = None
instagram_handler = None


def set_handlers(line=None, facebook=None, instagram=None):
    global line_handler, facebook_handler, instagram_handler
    line_handler = line
    facebook_handler = facebook
    instagram_handler = instagram


def get_line_handler() -> Optional[object]:
    return line_handler


def get_facebook_handler() -> Optional[object]:
    return facebook_handler


def get_instagram_handler() -> Optional[object]:
    return instagram_handler
