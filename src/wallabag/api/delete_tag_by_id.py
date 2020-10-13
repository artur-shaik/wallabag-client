# -*- coding: utf-8 -*-

from wallabag.api.api import Api, ApiMethod


class DeleteTagsById(Api):

    def __init__(self, config, tag_id):
        Api.__init__(self, config)
        self.tag_id = tag_id

    def _get_api_url(self):
        return self._build_url(
                ApiMethod.DELETE_TAG_BY_ID).format(self.tag_id)

    def _make_request(self, request):
        return self._request_delete(request)
