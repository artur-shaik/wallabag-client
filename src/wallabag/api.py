"""
Wallabag API accesses.
"""
import json
import re
import time
from enum import Enum, auto
from packaging import version

import requests

from wallabag.config import Options, Sections

MINIMUM_API_VERSION = 2, 1, 1
MINIMUM_API_VERSION_HR = "2.1.1"


class OAuthException(Exception):
    """
    An exception that occurs when the request of an oauth2-TOKEN fails.
    """
    def __init__(self, text):
        self.text = text


class Error(Enum):
    """
    A list of possible http errors.
    """
    UNDEFINED = -1
    OK = 0
    DNS_ERROR = 1
    HTTP_BAD_REQUEST = 400
    HTTP_UNAUTHORIZED = 401
    HTTP_FORBIDDEN = 403
    HTTP_NOT_FOUND = 404
    UNKNOWN_ERROR = 999


class ApiMethod(Enum):
    """
    The list of valid wallabag-api urls.
    The server url has to be put in front of it.
    """
    ADD_ENTRY = "/api/entries"
    DELETE_ENTRY = "/api/entries/{0}"
    GET_ENTRY = "/api/entries/{0}"
    UPDATE_ENTRY = "/api/entries/{0}"
    ENTRY_EXISTS = "/api/entries/exists"
    LIST_ENTRIES = "/api/entries"
    TOKEN = "/oauth/v2/token"
    VERSION = "/api/version"


class Verbs(Enum):
    GET = auto()
    POST = auto()
    PUT = auto()
    DELETE = auto()
    PATCH = auto()


class Response:
    """
    A response given by an api-call.
    """
    http_code = 0
    error = Error.UNDEFINED
    error_text = ""
    error_description = ""

    response = ""

    def __init__(self, status_code, http_response):
        self.http_code = status_code
        self.response = http_response

        # DNS not found
        if self.http_code == 0:
            self.error = Error.DNS_ERROR
            self.error_text = "Name or service not known."
        # 400 bad request
        elif self.http_code == 400:
            self.error = Error.HTTP_BAD_REQUEST
            errors = json.loads(self.response)
            if 'error' in errors:
                self.error_text = errors['error']
            if 'error_description' in errors:
                self.error_description = errors['error_description']
        # 401 unauthorized
        elif self.http_code == 401:
            self.error = Error.HTTP_UNAUTHORIZED
            errors = json.loads(self.response)
            if 'error' in errors:
                self.error_text = errors['error']
            if 'error_description' in errors:
                self.error_description = errors['error_description']
        # 403 forbidden
        elif self.http_code == 403:
            self.error = Error.HTTP_FORBIDDEN
            self.error_text = "403: Could not reach API due to rights issues."
        # 404 not found
        elif self.http_code == 404:
            self.error = Error.HTTP_NOT_FOUND
            self.error_text = "404: API was not found."
        # 200 okay
        elif self.http_code == 200:
            self.error = Error.OK
        # unknown Error
        else:
            self.error = Error.UNKNOWN_ERROR
            self.error_text = "An unknown error occured."

    def is_rersponse_status_ok(self):
        return self.http_code == 200

    def has_error(self):
        return self.error != Error.OK


class Api():

    VERSION_RE = re.compile('"\\d+\\.\\d+\\.\\d+"')

    def __init__(self, config):
        self.config = config

    def __get_api_url(self, api_method, url=None):
        if api_method in ApiMethod:
            serverurl = url or self.config.get(Sections.API, Options.SERVERURL)
            return serverurl + api_method.value
        return None

    def __get_authorization_header(self):
        success, token_or_error = self.get_token()
        if not success:
            return OAuthException(token_or_error)
        else:
            return {'Authorization': f"Bearer {token_or_error}"}

    def __make_request(self, type, url, headers=None, params=None, data=None):
        request = None

        try:
            request_methods = {
                Verbs.GET: requests.get,
                Verbs.DELETE: requests.delete,
                Verbs.POST: requests.post,
                Verbs.PATCH: requests.patch
            }

            request = request_methods[type](
                    url, headers=headers, params=params, data=data)
            return Response(request.status_code, request.text)
        except (
                requests.exceptions.ConnectionError,
                requests.exceptions.MissingSchema):
            return Response(0, None)

    def __request_delete(self, url, headers=None):
        return self.__make_request(Verbs.DELETE, url, headers)

    def __request_get(self, url, headers=None, params=None):
        return self.__make_request(
                Verbs.GET, url, headers=headers, params=params)

    def __request_post(self, url, headers=None, data=None):
        return self.__make_request(Verbs.POST, url, data=data, headers=headers)

    def __request_patch(self, url, headers=None, data=None):
        return self.__make_request(
                Verbs.PATCH, url, data=data, headers=headers)

    def is_valid_url(self, url):
        return not self.__request_get(url).has_error()

    def is_minimum_version(self, version_response):
        versionstring = version_response.response

        if not Api.VERSION_RE.match(versionstring):
            return False

        ver = versionstring.strip('"')
        return version.parse(MINIMUM_API_VERSION_HR) >= version.parse(ver)

    def api_version(self, different_url=None):
        url = self.__get_api_url(ApiMethod.VERSION, different_url)
        return self.__request_get(url)

    def api_token(self, ):
        url = self.__get_api_url(ApiMethod.TOKEN)
        data = {
            'grant_type': "password",
            'client_id': self.config.get(Sections.OAUTH2, Options.CLIENT),
            'client_secret': self.config.get(Sections.OAUTH2, Options.SECRET),
            'username': self.config.get(Sections.API, Options.USERNAME),
            'password': self.config.get(Sections.API, Options.PASSWORD)
        }
        return self.__request_get(url, params=data)

    def api_add_entry(self, targeturl, title=None, star=False, read=False):
        url = self.__get_api_url(ApiMethod.ADD_ENTRY)
        header = self.__get_authorization_header()
        data = {
            'url': targeturl
        }
        if title:
            data['title'] = title
        if star:
            data['starred'] = 1
        if read:
            data['archive'] = 1
        return self.__request_post(url, header, data)

    def api_delete_entry(self, entry_id):
        url = self.__get_api_url(ApiMethod.DELETE_ENTRY).format(entry_id)
        header = self.__get_authorization_header()

        return self.__request_delete(url, header)

    def api_entry_exists(self, url):
        url = self.__get_api_url(ApiMethod.ENTRY_EXISTS)
        header = self.__get_authorization_header()
        data = {
            'url': url
        }
        return self.__request_get(url, headers=header, params=data)

    def api_get_entry(self, entry_id):
        url = self.__get_api_url(ApiMethod.GET_ENTRY).format(entry_id)
        header = self.__get_authorization_header()
        return self.__request_get(url, header)

    def api_update_entry(self, entry_id, new_title=None, star=None, read=None):
        url = self.__get_api_url(ApiMethod.UPDATE_ENTRY).format(entry_id)
        header = self.__get_authorization_header()
        data = dict()
        if new_title:
            data['title'] = new_title
        if star is not None:
            data["starred"] = 1 if star else 0
        if read is not None:
            data['archive'] = 1 if read else 0
        return self.__request_patch(url, header, data)

    def api_list_entries(
            self, count, filter_read=None, filter_starred=None, oldest=False):
        url = self.__get_api_url(ApiMethod.LIST_ENTRIES)
        header = self.__get_authorization_header()
        params = {
            'perPage': count
        }

        if oldest:
            params['order'] = "asc"

        if filter_read is not None:
            params['archive'] = 1 if filter_read else 0

        if filter_starred is not None:
            params['starred'] = 1 if filter_starred else 0

        return self.__request_get(url, headers=header, params=params)

    def get_token(self, force_creation=False):
        if self.config.is_token_expired() or force_creation:
            response = self.api_token()
            if not response.has_error():
                content = json.loads(response.response)
                self.config.set(
                        Sections.TOKEN,
                        Options.ACCESS_TOKEN,
                        content['access_token'])
                self.config.set(
                        Sections.TOKEN,
                        Options.EXPIRES,
                        str(time.time() + content['expires_in']))
                self.config.save()
                return True, self.config.get(
                        Sections.TOKEN,
                        Options.ACCESS_TOKEN)
            else:
                if not response.error_description:
                    return False, response.error_text
                else:
                    error_text = response.error_text
                    error_description = response.error_description
                    return False, f"{error_text} - {error_description}"
        else:
            return True, self.config.get(
                    Sections.TOKEN,
                    Options.ACCESS_TOKEN)
