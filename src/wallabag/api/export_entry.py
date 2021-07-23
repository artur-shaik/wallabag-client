# -*- coding: utf-8 -*-

from wallabag.api.api import Api, ApiMethod, ValueException


class ExportEntry(Api):

    def __init__(self, config, entry_id, format):
        Api.__init__(self, config)
        self.entry_id = entry_id
        self.format = format

    def _get_api_url(self):
        entry_id = self._validate_identificator(self.entry_id)
        url = self._build_url(ApiMethod.GET_ENTRY).format(entry_id)
        if not self.format:
            raise ValueException('Format is not specified')
        if self.format == 'html':
            return url
        return f'{url}/export.{self.format}'

    def _make_request(self, request):
        return self._request_get(request)
