# -*- coding: utf-8 -*-

import os
import sys
import textwrap

import tabulate

from colorama import Fore

from wallabag.api.get_list_entries import (
        GetListEntries, Params as ListEntriesParams)
from wallabag.commands.command import Command
from wallabag.commands.params import Params
from wallabag.commands.tags_param import TagsParam
from wallabag.entry import Entry


class ListParams(Params, TagsParam):
    quantity = None
    filter_read = None
    filter_starred = None
    oldest = False
    trim = False
    tags = None

    def __init__(self, quantity=None, filter_read=None,
                 filter_starred=None, oldest=None, trim=None, tags=None):
        self.quantity = quantity
        self.filter_read = filter_read
        self.filter_starred = filter_starred
        self.oldest = oldest
        self.trim = trim
        self.tags = tags

    def validate(self):
        result, msg = self._validate_tags()
        if not result:
            return False, msg
        return True, None


class ListCommand(Command):

    def __init__(self, config, params=None):
        Command.__init__(self)
        self.config = config
        self.params = params or ListParams()

    def _run(self):
        api = GetListEntries(self.config, {
            ListEntriesParams.COUNT: self.__get_quantity(),
            ListEntriesParams.FILTER_READ: self.params.filter_read,
            ListEntriesParams.FILTER_STARRED: self.params.filter_starred,
            ListEntriesParams.OLDEST: self.params.oldest,
            ListEntriesParams.TAGS: self.params.tags
        })
        entries = Entry.create_list(
                api.request().response['_embedded']["items"])
        return True, self.__print_entries(entries)

    def __print_entries(self, entries):
        entry_id_width = self.__entry_id_width(entries)
        maxwidth = self.__get_maxwidth() - entry_id_width - 4
        output = []
        for item in entries:
            _maxwidth = maxwidth
            entry_id = str(item.entry_id).rjust(entry_id_width)

            status = self.__read_star_char(item)
            annotation_mark = self.__annotation_mark(item)
            tags_mark = self.__tags_mark(item)
            _maxwidth -= (2 if annotation_mark else 0)
            _maxwidth -= (2 if tags_mark else 0)
            title = textwrap.shorten(item.title, _maxwidth, placeholder='...')
            entry = [
                    entry_id, status,
                    f"{title}{annotation_mark}{tags_mark}"]
            output.append(entry)
        return tabulate.tabulate(output)

    def __get_quantity(self):
        if self.params.quantity is None:
            try:
                return os.get_terminal_size().lines - 3
            except OSError:
                return sys.maxsize
        else:
            return self.params.quantity

    def __get_maxwidth(self):
        if self.params.trim:
            try:
                return os.get_terminal_size().columns
            except OSError:
                pass
        return sys.maxsize

    def __entry_id_width(self, entries):
        if len(entries) > 0:
            size_entry_id = len(str(entries[0].entry_id))
            entry_id_last = len(str(entries[len(entries) - 1].entry_id))
            if entry_id_last > size_entry_id:
                size_entry_id = entry_id_last
            return size_entry_id
        return 0

    def __read_star_char(self, item):
        if item.starred:
            return "" if not item.read else ""
        return "" if not item.read else ""

    def __annotation_mark(self, entry):
        return f" {Fore.BLUE}{Fore.RESET}" if entry.annotations else ""

    def __tags_mark(self, entry):
        return f" {Fore.BLUE}{Fore.RESET}" if entry.tags else ""


class CountCommand(Command):

    def __init__(self, config, params=None):
        self.config = config
        self.params = params or ListParams()

    def _run(self):
        api = GetListEntries(self.config, {
            ListEntriesParams.COUNT: sys.maxsize,
            ListEntriesParams.FILTER_READ: self.params.filter_read,
            ListEntriesParams.FILTER_STARRED: self.params.filter_starred
        })
        response = api.request().response

        return True, len(response["_embedded"]["items"])
