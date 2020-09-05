"""
Wallabag API accesses.
"""
from enum import Enum
import json
import time
import re
import requests

from wallabag.config import Configs as conf


MINIMUM_API_VERSION = 2, 1, 1
MINIMUM_API_VERSION_HR = "2.1.1"


class OAuthException(Exception):
    """
    An exception that occurs when the request of an oauth2-token fails.
    """
    pass


class Error(Enum):
    """
    A list of possible http errors.
    """
    undefined = -1
    ok = 0
    dns_error = 1
    http_bad_request = 400
    http_unauthorized = 401
    http_forbidden = 403
    http_not_found = 404
    unknown_error = 999


class ApiMethod(Enum):
    """
    The list of valid wallabag-api urls.
    The server url has to be put in front of it.
    """
    add_entry = "/api/entries"
    delete_entry = "/api/entries/{0}"
    get_entry = "/api/entries/{0}"
    update_entry = "/api/entries/{0}"
    entry_exists = "/api/entries/exists"
    list_entries = "/api/entries"
    token = "/oauth/v2/token"
    version = "/api/version"


class Response:
    """
    A response given by an api-call.
    """
    http_code = 0
    error = Error.undefined
    error_text = ""
    error_description = ""

    response = ""

    def __init__(self, status_code, http_response):
        self.http_code = status_code
        self.response = http_response

        # DNS not found
        if self.http_code == 0:
            self.error = Error.dns_error
            self.error_text = "Name or service not known."
        # 400 bad request
        elif self.http_code == 400:
            self.error = Error.http_bad_request
            errors = json.loads(self.response)
            if 'error' in errors:
                self.error_text = errors['error']
            if 'error_description' in errors:
                self.error_description = errors['error_description']
        # 401 unauthorized
        elif self.http_code == 401:
            self.error = Error.http_unauthorized
            errors = json.loads(self.response)
            if 'error' in errors:
                self.error_text = errors['error']
            if 'error_description' in errors:
                self.error_description = errors['error_description']
        # 403 forbidden
        elif self.http_code == 403:
            self.error = Error.http_forbidden
            self.error_text = "403: Could not reach API due to rights issues."
        # 404 not found
        elif self.http_code == 404:
            self.error = Error.http_not_found
            self.error_text = "404: API was not found."
        # 200 okay
        elif self.http_code == 200:
            self.error = Error.ok
        # unknown Error
        else:
            self.error = Error.unknown_error
            self.error_text = "An unknown error occured."

    def is_rersponse_status_ok(self):
        """
        Return True if the http status code is ok.
        """
        return self.http_code == 200

    def has_error(self):
        """
        Returns True if the response has an error.
        """
        return self.error != Error.ok


def __get_api_url(api_method, different_url=None):
    if api_method in ApiMethod:
        if different_url != None:
            return different_url + api_method.value
        return Configs.serverurl + api_method.value
    return None


def __get_authorization_header():
    success, token_or_error = get_token()
    if not success:
        error = OAuthException
        error.text = token_or_error
        raise error
    else:
        return {'Authorization': "Bearer {0}".format(token_or_error)}


def __request_delete(url, headers=None):
    ret = None
    request = None

    try:
        request = requests.delete(url, headers=headers)
        ret = Response(request.status_code, request.text)
    # dns error
    except (requests.exceptions.ConnectionError, requests.exceptions.MissingSchema):
        ret = Response(0, None)
    return ret


def __request_get(url, headers=None, params=None):
    ret = None
    request = None

    try:
        request = requests.get(url, headers=headers, params=params)
        ret = Response(request.status_code, request.text)
    # dns error
    except (requests.exceptions.ConnectionError, requests.exceptions.MissingSchema):
        ret = Response(0, None)
    return ret


def __request_post(url, headers=None, data=None):
    ret = None
    request = None

    try:
        request = requests.post(url, data=data, headers=headers)
        ret = Response(request.status_code, request.text)
    # dns error
    except (requests.exceptions.ConnectionError, requests.exceptions.MissingSchema):
        ret = Response(0, None)
    return ret


def __request_patch(url, headers=None, data=None):
    ret = None
    request = None

    try:
        request = requests.patch(url, data=data, headers=headers)
        ret = Response(request.status_code, request.text)
    # dns error
    except (requests.exceptions.ConnectionError, requests.exceptions.MissingSchema):
        ret = Response(0, None)
    return ret


def is_valid_url(url):
    """
    Sends a request to the given url and checks if it returns a valid http page.
    """
    response = __request_get(url)
    return not response.has_error()


def is_minimum_version(version_response):
    """
    Returns True if the wallabag-instance meets the required minimum version.
    """
    versionstring = version_response.response
    print(versionstring)

    if not re.compile('"\\d+\\.\\d+\\.\\d+"').match(versionstring):
        return False

    ver = versionstring.strip('"').split('.')

    major = int(ver[0])
    minor = int(ver[1])
    patch = int(ver[2])
    tmajor, tminor, tpatch = MINIMUM_API_VERSION

    if major > tmajor:
        return True
    elif major < tmajor:
        return False
    else:
        if minor > tminor:
            return True
        elif minor < tminor:
            return False
        else:
            return patch >= tpatch


def api_version(different_url=None):
    """
    Returns the api version of the server saved in the config file.
    """
    url = __get_api_url(ApiMethod.version, different_url)
    response = __request_get(url)
    return response


def api_token():
    """
    Creates and returns a valid api-token
    """
    url = __get_api_url(ApiMethod.token)
    data = dict()
    data['grant_type'] = "password"
    data['client_id'] = Configs.client
    data['client_secret'] = Configs.secret
    data['username'] = Configs.username
    data['password'] = Configs.password

    response = __request_get(url, params=data)
    return response


def api_add_entry(targeturl, title=None, star=False, read=False):
    """
    Adds a new entry to the wallabag-account.
    """
    url = __get_api_url(ApiMethod.add_entry)
    header = __get_authorization_header()
    data = dict()
    data['url'] = targeturl
    if title != None:
        data['title'] = title
    if star:
        data['starred'] = 1
    if read:
        data['archive'] = 1
    response = __request_post(url, header, data)
    return response


def api_delete_entry(entry_id):
    """
    Deletes an existing entry from the wallabag-account.
    """
    url = __get_api_url(ApiMethod.delete_entry).format(entry_id)
    header = __get_authorization_header()

    response = __request_delete(url, header)
    return response


def api_entry_exists(url):
    """
    Checks if an entry already exists.
    """
    apiurl = __get_api_url(ApiMethod.entry_exists)
    header = __get_authorization_header()
    data = dict()
    data['url'] = url
    response = __request_get(apiurl, headers=header, params=data)
    return response


def api_get_entry(entry_id):
    """
    Gets an existing entry from the wallabag-account.
    """
    url = __get_api_url(ApiMethod.get_entry).format(entry_id)
    header = __get_authorization_header()

    response = __request_get(url, header)
    return response


def api_update_entry(entry_id, new_title=None, star=None, read=None):
    """
    Updates an existing entry.
    """
    url = __get_api_url(ApiMethod.update_entry).format(entry_id)
    header = __get_authorization_header()
    data = dict()
    if new_title != None:
        data['title'] = new_title
    if star != None:
        if not star:
            data['starred'] = 0
        else:
            data["starred"] = 1
    if read != None:
        if not read:
            data['archive'] = 0
        else:
            data['archive'] = 1
    response = __request_patch(url, header, data)
    return response


def api_list_entries(count, filter_read=None, filter_starred=None, oldest=False):
    """
    Gets a filtered list of existing entries.
    """
    url = __get_api_url(ApiMethod.list_entries)
    header = __get_authorization_header()
    params = dict()

    params['perPage'] = count

    if oldest:
        params['order'] = "asc"

    if filter_read != None:
        if filter_read:
            params['archive'] = 1
        else:
            params['archive'] = 0

    if filter_starred != None:
        if filter_starred:
            params['starred'] = 1
        else:
            params['starred'] = 0

    response = __request_get(url, headers=header, params=params)
    return response


def get_token(force_creation=False):
    """
    Returns a valid oauth token. Creates a new one if the old token is expired.

    Parameters:
    -----------
    force_creation [optional]bool
        Enforces the creation even if the old token is valid.

    Returns:
    --------
    bool
        Getting the token was successful.
    string
        A valid token or an error message.
    """
    if conf.is_token_expired() or force_creation:
        response = api_token()
        if not response.has_error():
            content = json.loads(response.response)
            Configs.access_token = content['access_token']
            Configs.expires = time.time() + content['expires_in']
            conf.save()
            return True, Configs.access_token
        else:
            if response.error_description == "":
                return False, response.error_text
            else:
                return False, "{0} - {1}".format(response.error_text, response.error_description)
    else:
        return True, Configs.access_token
