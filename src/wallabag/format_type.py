# -*- coding: utf-8 -*-

from enum import Enum, auto


class FormatType(Enum):
    XML = auto()
    JSON = auto()
    TXT = auto()
    CSV = auto()
    PDF = auto()
    EPUB = auto()
    MOBI = auto()
    HTML = auto()
    MARKDOWN = auto()
    UNSUPPORTED = auto()

    def list():
        return [c.name for c in FormatType]

    def get(name):
        for type in FormatType:
            if type.name == name.upper():
                return type
        return FormatType.UNSUPPORTED

    def extension(type):
        if type == FormatType.MARKDOWN:
            return 'md'
        elif type == FormatType.UNSUPPORTED:
            return ''
        return type.name.lower()


class ScreenType(Enum):
    TERM = auto()
    HTML = auto()
    MARKDOWN = auto()

    def list():
        return [c.name for c in ScreenType]

    def get(name):
        for type in ScreenType:
            if type.name == name.upper():
                return type
        return ScreenType.TERM

def format_to_screen(type):
    if type == FormatType.MARKDOWN:
        return ScreenType.MARKDOWN
    elif type == FormatType.HTML:
        return ScreenType.HTML
    else:
        return None
