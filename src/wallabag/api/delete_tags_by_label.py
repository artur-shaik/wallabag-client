# -*- coding: utf-8 -*-

from enum import Enum

from wallabag.api.api import Api, ApiMethod


class DeleteTagsByLabel(Api):

    class ApiParams(Enum):
        TAGS = "tags"

    def __init__(self, config, tags):
        Api.__init__(self, config)
        self.tags = tags

    def _get_api_url(self):
        return self._build_url(
                ApiMethod.DELETE_TAG_BY_LABEL)

    def _make_request(self, request):
        return self._request_delete(request)

    def _get_params(self):
        return {
            DeleteTagsByLabel.ApiParams.TAGS.value: self.tags
        }
