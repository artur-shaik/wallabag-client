"""
Module for deleting existing entries
"""
import json
from sys import exit

from . import api
from . import conf
from . import entry


def delete(entry_id, force=False, quiet=False):
    """
    Main function for deleting wallabag entries.
    """
    conf.load()

    if not force:
        try:
            request = api.api_get_entry(entry_id)
            __handle_request_error(request)
            entr = entry.Entry(json.loads(request.response))
            print("Do you really wish to delete the following entry?")
            i = input(entr.title + " [y/N] ")
            if str.lower(i) not in ["y", "yes"]:
                exit(0)
        except api.OAuthException as ex:
            print("Error: {0}".format(ex.text))
            print()
            exit(-1)

    try:
        request = api.api_delete_entry(entry_id)
        __handle_request_error(request)
        if not quiet:
            print("Entry successfully deleted.")
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
