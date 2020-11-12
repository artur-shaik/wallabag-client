import re
import json
import logging

from abc import ABC, abstractmethod
from enum import auto, Enum
from wallabag.config import Options, Sections

import requests

from packaging import version

MINIMUM_API_VERSION = "2.1.1"


class ApiException(Exception):

    error_text = None
    error_description = None

    def __init__(self, error_text=None, error_description=None):
        self.error_text = error_text
        self.error_description = error_description

    def __str__(self):
        desc = f"- {self.error_description}" if self.error_description else ""
        return f"Error: {self.error_text}{desc}"


class OAuthException(ApiException):
    pass


class RequestException(ApiException):

    def __init__(self, text=None, description=None, response=None):
        if response:
            ApiException.__init__(
                    self, response.error_text, response.error_description)
        else:
            ApiException.__init__(
                    self, text, description)
        self.response = response


class ValueException(ApiException):
    pass


class UnsupportedMethodException(ApiException):

    def __init__(self, method_name):
        self.error_text = 'Unsupported method called'
        self.error_description = f'Method: {method_name}'


class Error(Enum):
    UNDEFINED = -1
    OK = 0
    DNS_ERROR = 1
    HTTP_BAD_REQUEST = 400
    HTTP_UNAUTHORIZED = 401
    HTTP_FORBIDDEN = 403
    HTTP_NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    UNKNOWN_ERROR = 999


class ApiMethod(Enum):
    ADD_ENTRY = "/api/entries"
    DELETE_ENTRY = "/api/entries/{0}"
    GET_ENTRY = "/api/entries/{0}"
    UPDATE_ENTRY = "/api/entries/{0}"
    ENTRY_EXISTS = "/api/entries/exists"
    LIST_ENTRIES = "/api/entries"
    ADD_TAGS_TO_ENTRY = "/api/entries/{0}/tags"
    GET_TAGS = "/api/tags"
    GET_TAGS_FOR_ENTRY = "/api/entries/{0}/tags"
    DELETE_TAG_FROM_ENTRY = "/api/entries/{0}/tags/{1}"
    DELETE_TAG_BY_ID = "/api/tags/{0}"
    DELETE_TAG_BY_LABEL = "/api/tags/label"
    DELETE_ANNOTATION = "/api/annotations/{0}"
    TOKEN = "/oauth/v2/token"
    VERSION = "/api/version"


class Verbs(Enum):
    GET = auto()
    POST = auto()
    PUT = auto()
    DELETE = auto()
    PATCH = auto()
    HEAD = auto()


class Response:
    error = Error.UNDEFINED
    error_text = ""
    error_description = ""

    response = None

    def __init__(self, status_code, text=None):
        if text:
            try:
                self.response = json.loads(text)
            except json.decoder.JSONDecodeError as err:
                self.error_text = str(err)
                self.response = text
        errors = {
            0: (Error.DNS_ERROR, ("Name or service not known.", None)),
            400: (Error.HTTP_BAD_REQUEST, self.__error_from_server),
            401: (Error.HTTP_UNAUTHORIZED, self.__error_from_server),
            403: (Error.HTTP_FORBIDDEN,
                  ("403: Could not reach API due to rights issues.", None)),
            404: (Error.HTTP_NOT_FOUND, ("404: API was not found.", None)),
            405: (Error.METHOD_NOT_ALLOWED,
                  ("405: Method not allowed.", None)),
            200: (Error.OK, None),
            418: (Error.OK, None),
        }

        if status_code in errors:
            result = errors.get(status_code)
        else:
            result = (Error.UNKNOWN_ERROR,
                      (f"An unknown error occured. {status_code}", None))

        self.error = result[0]
        if isinstance(result[1], tuple):
            self.error_text = result[1][0]
            self.error_description = result[1][1]
        elif result[1]:
            (self.error_text, self.error_description) = result[1]()

    def has_error(self):
        return self.error != Error.OK

    def __error_from_server(self):
        return (self.response['error'] if 'error' in self.response else None,
                self.response['error_description']
                if 'error_description' in self.response else None)


class Api(ABC):

    VERSION_RE = re.compile('\\d+\\.\\d+\\.\\d+')
    URL_RE = re.compile("(?i)https?:\\/\\/.+")
    HEAD_UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
    REQUEST_METHODS = {
        Verbs.GET: requests.get,
        Verbs.DELETE: requests.delete,
        Verbs.POST: requests.post,
        Verbs.PATCH: requests.patch,
        Verbs.HEAD: requests.head
    }

    class Request:
        type = None
        url = None
        api_params = None
        headers = None
        data = None

    skip_auth = False

    def __init__(self, config):
        self.log = logging.getLogger('wallabag.api')
        self.config = config

    def request(self):
        self.log.debug('making api request: %s', self.__class__.__name__)
        request = Api.Request()
        request.url = self._get_api_url()
        if not self.skip_auth:
            request.headers = self._get_authorization_header()
        request.api_params = self._get_params()
        request.data = self._get_data()
        return self._make_request(request)

    def is_minimum_version(version_response):
        versionstring = version_response.response

        if not Api.VERSION_RE.match(versionstring):
            return False

        ver = versionstring.strip('"')
        return version.parse(MINIMUM_API_VERSION) <= version.parse(ver)

    def _build_url(self, api_method, url=None):
        try:
            if api_method in ApiMethod:
                serverurl = url or self.config.get(
                        Sections.API, Options.SERVERURL)
                return serverurl + api_method.value
        except TypeError:
            raise UnsupportedMethodException(api_method)

    def _request_delete(self, request):
        request.type = Verbs.DELETE
        return self.__make_request(request)

    def _request_head(self, request):
        request.type = Verbs.HEAD
        return self.__make_request(request)

    def _request_get(self, request):
        request.type = Verbs.GET
        return self.__make_request(request)

    def _request_post(self, request):
        request.type = Verbs.POST
        return self.__make_request(request)

    def _request_patch(self, request):
        request.type = Verbs.PATCH
        return self.__make_request(request)

    def _is_valid_url(self, url):
        try_method_get = False
        while True:
            request = Api.Request()
            request.url = url
            request.headers = {'user-agent': Api.HEAD_UA}
            if not try_method_get:
                result = self._request_head(request)
                if result.error == Error.METHOD_NOT_ALLOWED:
                    try_method_get = True
                    continue
            else:
                result = self._request_get(request)
            break
        return not result.has_error()

    def _validate_url(self, url):
        if not url:
            raise ValueException("Invalid url")
        if not Api.URL_RE.match(url):
            for protocol in "https://", "http://":
                if self._is_valid_url(f"{protocol}{url}"):
                    url = f"{protocol}{url}"
                    valid_url = True
                    break
        else:
            valid_url = self._is_valid_url(url)

        if not valid_url:
            raise ValueException("Invalid url")
        return url

    def _validate_identificator(self, entry_id):
        if not entry_id:
            raise ValueException("ENTRY_ID is not a number")

        try:
            entry_id = int(entry_id)
        except ValueError:
            raise ValueException("ENTRY_ID is not a number")

        if entry_id < 0:
            raise ValueException("ENTRY_ID is less than zero")

        return entry_id

    def _put_bool_param(self, api_params, param, api_param):
        if self.params[param] is not None:
            if isinstance(self.params[param], bool):
                api_params[api_param.value] = 1 if self.params[param] else 0

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

    def _get_authorization_header(self):
        from wallabag.configurator import TokenConfigurator

        token = TokenConfigurator(self.config).get_token()
        return {'Authorization': f"Bearer {token}"}

    def __make_request(self, request):
        try:
            self.log.debug('request data: %s', request.__dict__)

            result = Api.REQUEST_METHODS[request.type](
                    request.url, headers=request.headers,
                    params=request.api_params, data=request.data,
                    allow_redirects=True)
            response = Response(result.status_code, result.text)
        except (
                requests.exceptions.ConnectionError,
                requests.exceptions.MissingSchema) as error:
            self.log.exception('request exception')
            raise RequestException(
                    'Connection error', error)

        self.log.debug('response result: %s', response.__dict__)

        if response.has_error():
            raise RequestException(response=response)
        return response
