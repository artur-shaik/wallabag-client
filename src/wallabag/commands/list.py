# -*- coding: utf-8 -*-

import os
import platform
import sys

from wallabag.api.api import ApiException
from wallabag.api.get_list_entries import GetListEntries, Params
from wallabag.commands.command import Command
from wallabag.entry import Entry


class ListParams():
    quantity = None
    filter_read = None
    filter_starred = None
    oldest = False
    trim = True

    def __init__(self, quantity=None, filter_read=None,
                 filter_starred=None, oldest=None, trim=None):
        self.quantity = quantity
        self.filter_read = filter_read
        self.filter_starred = filter_starred
        self.oldest = oldest
        self.trim = trim


class ListCommand(Command):

    def __init__(self, config, params=None):
        self.config = config
        self.params = params or ListParams()

    def run(self):
        try:
            api = GetListEntries(self.config, {
                Params.COUNT: self.__get_quantity(),
                Params.FILTER_READ: self.params.filter_read,
                Params.FILTER_STARRED: self.params.filter_starred,
                Params.OLDEST: self.params.oldest
            })
            entries = Entry.create_list(
                    api.request().response['_embedded']["items"])
            return True, self.__print_entries(entries)
        except ApiException as ex:
            return False, str(ex)

    def __print_entries(self, entries):
        show_read_column, show_starred_column = self.__read_star_width(entries)
        entry_id_width = self.__entry_id_width(entries)
        maxwidth = self.__get_maxwidth()
        output = []
        if not self.params.oldest:
            entries = reversed(entries)
        for item in entries:
            entry_id = str(item.entry_id).rjust(entry_id_width)

            title = item.title
            read, starred = self.__read_star_char(item)
            line = entry_id
            if show_read_column or show_starred_column:
                line = line + " "
                if show_read_column:
                    line = line + read
                if show_starred_column:
                    line = line + starred

            line = f"{line} {title}"
            output.append(line[0:maxwidth])
        return '\n'.join(output)

    def __get_quantity(self):
        if self.params.quantity is None:
            try:
                return os.get_terminal_size().lines - 2
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

    def __read_star_width(self, entries):
        show_read_column = False
        show_starred_column = False
        for item in entries:
            if item.read:
                show_read_column = True
            if item.starred:
                show_starred_column = True
            if show_read_column and show_starred_column:
                break
        return (show_read_column, show_starred_column)

    def __read_star_char(self, item):
        read = " "
        if item.read:
            if platform.system() == "Windows":
                read = "r"
            else:
                read = "✔"

        starred = " "
        if item.starred:
            starred = "*"

        return (read, starred)


class CountCommand(Command):

    def __init__(self, config, params=None):
        self.config = config
        self.params = params or ListParams()

    def run(self):
        try:
            api = GetListEntries(self.config, {
                Params.COUNT: sys.maxsize,
                Params.FILTER_READ: self.params.filter_read,
                Params.FILTER_STARRED: self.params.filter_starred
            })
            response = api.request().response
        except ApiException as ex:
            return False, str(ex)

        return True, len(response["_embedded"]["items"])
