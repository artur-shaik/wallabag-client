# -*- coding: utf-8 -*-

from wallabag.api.api import Api, ApiMethod


class DeleteTagFromEntry(Api):

    def __init__(self, config, entry_id, tag):
        Api.__init__(self, config)
        self.entry_id = entry_id
        self.tag = tag

    def _get_api_url(self):
        entry_id = self._validate_identificator(self.entry_id)
        return self._build_url(
                ApiMethod.DELETE_TAG_FROM_ENTRY).format(entry_id, self.tag)

    def _make_request(self, request):
        return self._request_delete(request)
