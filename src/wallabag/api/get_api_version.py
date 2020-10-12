# -*- coding: utf-8 -*-

from wallabag.api.api import Api, ApiMethod


class ApiVersion(Api):

    def __init__(self, config, custom_url=None):
        Api.__init__(self, config)
        self.custom_url = custom_url
        self.skip_auth = True

    def _get_api_url(self):
        return self._build_url(ApiMethod.VERSION, self.custom_url)

    def _make_request(self, request):
        return self._request_get(request)
