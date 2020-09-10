"""
Wallabag API accesses.
"""
import json
import re
import time
from abc import ABC, abstractmethod
from enum import Enum, auto

from packaging import version

import requests

from wallabag.config import Options, Sections

MINIMUM_API_VERSION = 2, 1, 1
MINIMUM_API_VERSION_HR = "2.1.1"


class ApiException(Exception):

    error_text = None
    error_description = None

    def __init__(self, error_text=None, error_description=None):
        self.error_text = error_text
        self.error_description = error_description


class OAuthException(ApiException):
    pass


class RequestException(ApiException):
    pass


class ValueException(ApiException):
    pass


class UnsupportedMethodException(ApiException):

    def __init__(self, method_name):
        self.error_text = 'Unsupported method called'
        self.error_description = f'Method: {method_name}'


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

    def __init__(self, response):
        self.http_code = response.status_code
        self.response = response.text

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


class Api(ABC):

    VERSION_RE = re.compile('"\\d+\\.\\d+\\.\\d+"')

    class Request:
        type = None
        url = None
        api_params = None
        headers = None
        data = None

    def __init__(self, config):
        self.config = config

    def _build_url(self, api_method, url=None):
        try:
            if api_method in ApiMethod:
                serverurl = url or self.config.get(
                        Sections.API, Options.SERVERURL)
                return serverurl + api_method.value
        except TypeError:
            raise UnsupportedMethodException(api_method)

    def __get_authorization_header(self):
        success, token_or_error = self.get_token()
        if not success:
            return OAuthException(token_or_error)
        else:
            return {'Authorization': f"Bearer {token_or_error}"}

    def __make_request(self, request):
        try:
            request_methods = {
                Verbs.GET: requests.get,
                Verbs.DELETE: requests.delete,
                Verbs.POST: requests.post,
                Verbs.PATCH: requests.patch
            }

            response = Response(request_methods[request.type](
                    request.url, headers=request.headers,
                    params=request.api_params, data=request.data))
            if response.has_error():
                raise RequestException(
                        response.error_text, response.error_description)
            return response
        except (
                requests.exceptions.ConnectionError,
                requests.exceptions.MissingSchema):
            return Response(0, None)

    def __request_delete(self, url, headers=None):
        return self.__make_request(Verbs.DELETE, url, headers)

    def _request_get(self, request):
        request.type = Verbs.GET
        return self.__make_request(request)

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

    def api_token(self):
        request = Api.Request()
        request.url = self._build_url(ApiMethod.TOKEN)
        request.api_params = {
            'grant_type': "password",
            'client_id': self.config.get(Sections.OAUTH2, Options.CLIENT),
            'client_secret': self.config.get(Sections.OAUTH2, Options.SECRET),
            'username': self.config.get(Sections.API, Options.USERNAME),
            'password': self.config.get(Sections.API, Options.PASSWORD)
        }
        return self._request_get(request)

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

    @abstractmethod
    def _make_request(self, request):
        pass

    @abstractmethod
    def _get_api_url(self):
        pass

    def _get_params(self):
        return None

    def _get_data(self):
        return None

    def request(self):
        request = Api.Request()
        request.url = self._get_api_url()
        request.headers = self.__get_authorization_header()
        request.api_params = self._get_params()
        request.data = self._get_data()
        return self._make_request(request)

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
