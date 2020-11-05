# -*- coding: utf-8 -*-

from enum import Enum

from wallabag.api.api import Api, ApiMethod, ValueException


class Params(Enum):
    ENTRY_ID = "entry_id"
    TAGS = "tags"


class AddTagToEntry(Api):

    class ApiParams(Enum):
        TAGS = "tags"

    def __init__(self, config, params):
        Api.__init__(self, config)
        self.params = params

    def _make_request(self, request):
        return self._request_post(request)

    def _get_api_url(self):
        entry_id = self._validate_identificator(self.params[Params.ENTRY_ID])
        return self._build_url(ApiMethod.ADD_TAGS_TO_ENTRY).format(entry_id)

    def _get_data(self):
        if Params.TAGS not in self.params:
            raise ValueException(f"{Params.TAGS.value} is empty")
        return {
            AddTagToEntry.ApiParams.TAGS.value: self.params[Params.TAGS]
        }
