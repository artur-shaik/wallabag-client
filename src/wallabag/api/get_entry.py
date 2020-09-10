# -*- coding: utf-8 -*-

from wallabag.api.api import Api, ApiMethod, ValueException


class GetEntry(Api):

    def __init__(self, config, entry_id):
        Api.__init__(self, config)
        self.entry_id = entry_id

    def _get_api_url(self):
        if not self.entry_id:
            raise ValueException("ENTRY_ID is not a number")

        try:
            self.entry_id = int(self.entry_id)
        except ValueError:
            raise ValueException("ENTRY_ID is not a number")

        if self.entry_id < 0:
            raise ValueException("ENTRY_ID is less than zero")

        return self._build_url(ApiMethod.GET_ENTRY).format(self.entry_id)

    def _make_request(self, request):
        return self._request_get(request)
