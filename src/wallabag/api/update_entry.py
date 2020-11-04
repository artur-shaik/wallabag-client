# -*- coding: utf-8 -*-

from enum import Enum

from wallabag.api.api import Api, ApiMethod, ValueException


class Params(Enum):
    TITLE = "title"
    STAR = "star"
    READ = "read"


class UpdateEntry(Api):

    API_METHOD = ApiMethod.UPDATE_ENTRY

    class ApiParams(Enum):
        TITLE = "title"
        STARRED = "starred"
        ARCHIVE = "archive"

    def __init__(self, config, entry_id, params):
        Api.__init__(self, config)
        self.entry_id = entry_id
        self.params = params

    def _make_request(self, request):
        return self._request_patch(request)

    def _get_api_url(self):
        entry_id = self._validate_identificator(self.entry_id)
        return self._build_url(UpdateEntry.API_METHOD).format(entry_id)

    def _get_data(self):
        ApiParams = self.ApiParams
        data = {}
        if Params.TITLE in self.params and self.params[Params.TITLE]:
            data[ApiParams.TITLE.value] = self.params[Params.TITLE]
        if Params.STAR in self.params:
            self._put_bool_param(data, Params.STAR, ApiParams.STARRED)
        if Params.READ in self.params:
            self._put_bool_param(data, Params.READ, ApiParams.ARCHIVE)
        if not data:
            raise ValueException("The data object is empty")
        return data
