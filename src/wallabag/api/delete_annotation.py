# -*- coding: utf-8 -*-

from wallabag.api.api import Api, ApiMethod


class DeleteAnnotation(Api):

    def __init__(self, config, anno_id):
        Api.__init__(self, config)
        self.anno_id = anno_id

    def _get_api_url(self):
        anno_id = self._validate_identificator(self.anno_id)
        return self._build_url(
                ApiMethod.DELETE_ANNOTATION).format(anno_id)

    def _make_request(self, request):
        return self._request_delete(request)
