"""
Module for updating existing entries
"""
import json
from sys import exit

from wallabag.api.api import ApiException
from wallabag.api.get_entry import GetEntry
from wallabag.api.update_entry import UpdateEntry, Params
from . import entry


def update(config, entry_id, toggle_read=False,
           toggle_star=False, new_title=None, quiet=False):
    read_value = None
    star_value = None

    try:
        api = GetEntry(config, entry_id)
        request = api.request()
        __handle_request_error(request)
        entr = entry.Entry(json.loads(request.response))
        if toggle_read:
            read_value = not entr.read
        if toggle_star:
            star_value = not entr.starred
    except ApiException as ex:
        print(f"Error: {ex.error_text} - {ex.error_description}")
        print()
        exit(-1)

    try:
        api = UpdateEntry(config, entry_id, {
            Params.TITLE: new_title,
            Params.STAR: star_value,
            Params.READ: read_value
        })
        request = api.request()
        __handle_request_error(request)
        if not quiet:
            print("Entry successfully updated.")
            print()
        exit(0)
    except ApiException as ex:
        print(f"Error: {ex.error_text} - {ex.error_description}")
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
