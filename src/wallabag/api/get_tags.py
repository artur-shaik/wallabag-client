# -*- coding: utf-8 -*-

from wallabag.api.api import Api, ApiMethod


class GetTags(Api):

    def __init__(self, config):
        Api.__init__(self, config)

    def _get_api_url(self):
        return self._build_url(ApiMethod.GET_TAGS)

    def _make_request(self, request):
        return self._request_get(request)
