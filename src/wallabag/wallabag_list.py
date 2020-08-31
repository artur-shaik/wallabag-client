"""
List existing entries
"""
import json
import os
import platform
import sys
from sys import exit

from . import api
from . import conf
from . import entry


def list_entries(custom_quantity=None, filter_read=False, filter_starred=None, oldest=False, trim=True):
    """
    Main function for listing wallabag entries.
    """
    conf.load()

    quantity = None
    if custom_quantity is None:
        try:
            quantity = os.get_terminal_size().lines - 2
        # piped output to file or other process
        except OSError:
            quantity = sys.maxsize
    else:
        quantity = custom_quantity

    try:
        request = api.api_list_entries(
            quantity, filter_read, filter_starred, oldest)
        if request.has_error():
            print("Error: {0} - {1}".format(request.error_text,
                                            request.error_description))
            exit(-1)
        response = json.loads(request.response)
    except api.OAuthException as ex:
        print("Error: {0}".format(ex.text))
        print()
        exit(-1)

    entries = entry.entrylist(response['_embedded']["items"])
    print_entries(entries, trim, (not oldest))


def count_entries(filter_read=False, filter_starred=None):
    """
    Prints the number of entries to the standard output.
    """
    conf.load()

    try:
        request = api.api_list_entries(
            sys.maxsize, filter_read, filter_starred)
        if request.has_error():
            print("Error: {0} - {1}".format(request.error_text,
                                            request.error_description))
            exit(-1)
        response = json.loads(request.response)
    except api.OAuthException as ex:
        print("Error: {0}".format(ex.text))
        print()
        exit(-1)
    print(len(response["_embedded"]["items"]))


def print_entries(entries, trim, reverse_order=False):
    """
    Builds the output and prints all entries.
    """
    maxlength = sys.maxsize
    if trim:
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

    if reverse_order:
        entries = reversed(entries)
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
        print(line[0:maxlength])
