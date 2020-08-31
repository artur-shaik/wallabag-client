"""
Module for adding new entries
"""
import json
import re
from sys import exit

from . import api
from . import conf


def add(target_url, title=None, star=False, read=False, quiet=False):
    """
    Main function for adding new entries to the wallabag account.
    """
    conf.load()

    valid_url = False
    if not re.compile("(?i)https?:\\/\\/.+").match(target_url):
        for protocol in "https://", "http://":
            if api.is_valid_url("{0}{1}".format(protocol, target_url)):
                target_url = "{0}{1}".format(protocol, target_url)
                valid_url = True
                break
    else:
        valid_url = api.is_valid_url(target_url)

    if not valid_url:
        print("Error: Invalid url.")
        print()
        exit(-1)

    try:
        request = api.api_entry_exists(target_url)
        if request.has_error():
            print("Error: {0} - {1}".format(request.error_text,
                                            request.error_description))
            print()
            exit(-1)
        response = json.loads(request.response)
        if response['exists']:
            if not quiet:
                print("The url was already saved.")
            exit(0)

    except api.OAuthException as ex:
        print("Error: {0}".format(ex.text))
        print()
        exit(-1)

    try:
        request = api.api_add_entry(target_url, title, star, read)
        if request.has_error():
            print("Error: {0} - {1}".format(request.error_text,
                                            request.error_description))
            print()
            exit(-1)
        else:
            if not quiet:
                print("Entry successfully added.")
            exit(0)
    except api.OAuthException as ex:
        print("Error: {0}".format(ex.text))
        print()
        exit(-1)
