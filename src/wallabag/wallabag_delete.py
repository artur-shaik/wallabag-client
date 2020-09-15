from sys import exit

from wallabag.api.api import ApiException, Error
from wallabag.api.get_entry import GetEntry
from wallabag.api.delete_entry import DeleteEntry
from . import entry


def delete(config, entry_id, force=False, quiet=False):
    if not force:
        try:
            api = GetEntry(config, entry_id)
            request = api.request()
            __handle_request_error(request)
            entr = entry.Entry(request.response)
            print("Do you really wish to delete the following entry?")
            i = input(entr.title + " [y/N] ")
            if str.lower(i) not in ["y", "yes"]:
                exit(0)
        except ApiException as ex:
            print(f"Error: {ex.error_text} - {ex.error_description}")
            print()
            exit(-1)

    try:
        api = DeleteEntry(config, entry_id)
        request = api.request()
        __handle_request_error(request)
        if not quiet:
            print("Entry successfully deleted.")
            print()
        exit(0)
    except ApiException as ex:
        print(f"Error: {ex.error_text} - {ex.error_description}")
        print()
        exit(-1)


def __handle_request_error(request):
    if request.has_error():
        if request.error == Error.http_forbidden or request.error == Error.http_not_found:
            print("Error: Invalid entry id.")
            print()
            exit(-1)
        print("Error: {0} - {1}".format(request.error_text,
                                        request.error_description))
        exit(-1)
