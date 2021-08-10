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
    CLI = auto()
    MARKDOWN = auto()

    def list():
        return [c.name for c in FormatType]

    def get(name):
        for format in FormatType:
            if format.name == name.upper():
                return format
        return FormatType.JSON


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
