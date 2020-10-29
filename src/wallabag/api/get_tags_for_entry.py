# -*- coding: utf-8 -*-

from wallabag.api.api import Api, ApiMethod


class GetTagsForEntry(Api):

    def __init__(self, config, entry_id):
        Api.__init__(self, config)
        self.entry_id = entry_id

    def _get_api_url(self):
        entry_id = self._validate_identificator(self.entry_id)
        return self._build_url(ApiMethod.GET_TAGS_FOR_ENTRY).format(entry_id)

    def _make_request(self, request):
        return self._request_get(request)
