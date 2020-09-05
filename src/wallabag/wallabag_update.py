"""
Module for updating existing entries
"""
import json
from sys import exit

from . import api
from . import entry
from wallabag.config import Configs as conf


def update(entry_id, toggle_read=False, toggle_star=False, new_title=None, quiet=False):
    """
    Main method for updating existing wallabag entries.
    """
    conf.load()

    read_value = None
    star_value = None

    try:
        request = api.api_get_entry(entry_id)
        __handle_request_error(request)
        entr = entry.Entry(json.loads(request.response))
        if toggle_read and entr.read:
            read_value = 0
        elif toggle_read and not entr.read:
            read_value = 1
        if toggle_star and entr.starred:
            star_value = 0
        elif toggle_star and not entr.starred:
            star_value = 1
    except api.OAuthException as ex:
        print("Error: {0}".format(ex.text))
        print()
        exit(-1)

    try:
        request = api.api_update_entry(
            entry_id, new_title, star_value, read_value)
        __handle_request_error(request)
        if not quiet:
            print("Entry successfully updated.")
            print()
        exit(0)
    except api.OAuthException as ex:
        print("Error: {0}".format(ex.text))
        print()
        exit(-1)


def __handle_request_error(request):
    if request.has_error():
        if request.error == api.Error.http_forbidden or request.error == api.Error.http_not_found:
            print("Error: Invalid entry id.")
            print()
            exit(-1)
        print("Error: {0} - {1}".format(request.error_text,
                                        request.error_description))
        exit(-1)
