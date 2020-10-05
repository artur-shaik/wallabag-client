# -*- coding: utf-8 -*-

from enum import Enum

from wallabag.api.api import Api, ApiMethod, ValueException


class Params(Enum):
    TITLE = "title"
    STARRED = "starred"
    READ = "read"
    TAGS = "tags"


class AddEntry(Api):

    API_METHOD = ApiMethod.ADD_ENTRY

    class ApiParams(Enum):
        URL = "url"
        TITLE = "title"
        STARRED = "starred"
        ARCHIVE = "archive"
        TAGS = "tags"

    def __init__(self, config, url, params):
        Api.__init__(self, config)
        self.url = url
        self.params = params

    def _make_request(self, request):
        return self._request_post(request)

    def _get_api_url(self):
        return self._build_url(AddEntry.API_METHOD)

    def _get_data(self):
        ApiParams = self.ApiParams
        data = {
            ApiParams.URL.value: self._validate_url(self.url)
        }
        if Params.TITLE in self.params and self.params[Params.TITLE]:
            data[ApiParams.TITLE.value] = self.params[Params.TITLE]
        if Params.STARRED in self.params:
            self._put_bool_param(data, Params.STARRED, ApiParams.STARRED)
        if Params.READ in self.params:
            self._put_bool_param(data, Params.READ, ApiParams.ARCHIVE)
        if Params.TAGS in self.params:
            data[ApiParams.TAGS.value] = self.params[Params.TAGS]
        if not data:
            raise ValueException("The data object is empty")
        return data
