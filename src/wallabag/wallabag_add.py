"""
Module for adding new entries
"""
from sys import exit

from wallabag.api.api import ApiException
from wallabag.api.add_entry import AddEntry, Params
from wallabag.api.entry_exists import EntryExists


def add(config, target_url, title=None, star=False, read=False, quiet=False):
    try:
        api = EntryExists(config, target_url)
        response = api.request().response
        if response['exists']:
            if not quiet:
                print("The url was already saved.")
            exit(0)

        api = AddEntry(config, target_url, {
            Params.TITLE: title,
            Params.READ: read,
            Params.STAR: star
        })
        api.request()
        if not quiet:
            print("Entry successfully added.")
    except ApiException as ex:
        print(f"Error: {ex.error_text} - {ex.error_description}")
        print()
        exit(-1)
