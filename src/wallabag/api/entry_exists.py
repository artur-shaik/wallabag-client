# -*- coding: utf-8 -*-

from enum import Enum

from wallabag.api.api import Api, ApiMethod, ValueException


class EntryExists(Api):

    API_METHOD = ApiMethod.ENTRY_EXISTS

    class ApiParams(Enum):
        URL = "url"

    def __init__(self, config, url):
        Api.__init__(self, config)
        self.url = url

    def _make_request(self, request):
        return self._request_get(request)

    def _get_api_url(self):
        return self._build_url(EntryExists.API_METHOD)

    def _get_params(self):
        if not self.url:
            raise ValueException("URL is empty")
        return {
            EntryExists.ApiParams.URL.value: self.url
        }
