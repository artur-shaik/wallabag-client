# -*- coding: utf-8 -*-

import os
import platform
import sys

from wallabag.api.api import ApiException
from wallabag.api.get_list_entries import GetListEntries, Params
from wallabag.commands.command import Command
from wallabag.entry import Entry


class ListParams():
    custom_quantity = None
    filter_read = None
    filter_starred = None
    oldest = False
    trim = True

    def __init__(self, custom_quantity, filter_read,
                 filter_starred, oldest, trim):
        self.custom_quantity = custom_quantity
        self.filter_read = filter_read
        self.filter_starred = filter_starred
        self.oldest = oldest
        self.trim = trim


class ListCommand(Command):

    def __init__(self, config, params=None):
        self.config = config
        self.params = params or ListParams()

    def run(self):
        quantity = None
        if self.params.custom_quantity is None:
            try:
                quantity = os.get_terminal_size().lines - 2
            # piped output to file or other process
            except OSError:
                quantity = sys.maxsize
        else:
            quantity = self.params.custom_quantity

        try:
            api = GetListEntries(self.config, {
                Params.COUNT: quantity,
                Params.FILTER_READ: self.params.filter_read,
                Params.FILTER_STARRED: self.params.filter_starred,
                Params.OLDEST: self.params.oldest
            })
            request = api.request()
            response = request.response
        except ApiException as ex:
            return False, f"Error: {ex.error_text} - {ex.error_description}"

        entries = Entry.entrylist(response['_embedded']["items"])
        return True, self.print_entries(entries)

    def print_entries(self, entries):
        maxlength = sys.maxsize
        if self.params.trim:
            try:
                maxlength = os.get_terminal_size().columns
            # piped output to file or other process
            except OSError:
                maxlength = sys.maxsize
        size_entry_id = 0
        show_read_column = False
        show_starred_column = False
        if len(entries) > 0:
            size_entry_id = len(str(entries[0].entry_id))
            entry_id_last = len(str(entries[len(entries) - 1].entry_id))
            if entry_id_last > size_entry_id:
                size_entry_id = entry_id_last

        for item in entries:
            if item.read:
                show_read_column = True
            if item.starred:
                show_starred_column = True

        if not self.params.oldest:
            entries = reversed(entries)
        output = []
        for item in entries:
            entry_id = str(item.entry_id).rjust(size_entry_id)

            read = " "
            if item.read:
                if platform.system() == "Windows":
                    read = "r"
                else:
                    read = "✔"

            starred = " "
            if item.starred:
                starred = "*"

            title = item.title

            line = entry_id
            if show_read_column or show_starred_column:
                line = line + " "
                if show_read_column:
                    line = line + read
                if show_starred_column:
                    line = line + starred

            line = line + " {0}".format(title)
            output.append(line[0:maxlength])
        return '\n'.join(output)


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
            return False, f"Error: {ex.error_text} - {ex.error_description}"

        return True, len(response["_embedded"]["items"])
