# -*- coding: utf-8 -*-

from enum import Enum

from wallabag.api.api import Api, ApiMethod


class Params(Enum):
    COUNT = "count"
    FILTER_READ = "filter_read"
    FILTER_STARRED = "filter_starred"
    OLDEST = "oldest"
    TAGS = "tags"


class GetListEntries(Api):

    API_METHOD = ApiMethod.LIST_ENTRIES

    class ApiParams(Enum):
        PER_PAGE = "perPage"
        ORDER = "order"
        ARCHIVE = "archive"
        STARRED = "starred"
        TAGS = "tags"

    class ApiValues(Enum):
        class ORDER(Enum):
            ASC = "asc"

    def __init__(self, config, params):
        Api.__init__(self, config)
        self.params = params

    def _make_request(self, request):
        return self._request_get(request)

    def _get_api_url(self):
        return self._build_url(GetListEntries.API_METHOD)

    def _get_params(self):
        ApiParams = self.ApiParams
        ApiValues = self.ApiValues
        count = self.__get_count(self.params[Params.COUNT])
        api_params = {
            ApiParams.PER_PAGE.value: count
        }

        if Params.OLDEST in self.params and self.params[Params.OLDEST]:
            api_params[ApiParams.ORDER.value] = ApiValues.ORDER.value.ASC.value

        if Params.FILTER_READ in self.params:
            self._put_bool_param(
                    api_params, Params.FILTER_READ, ApiParams.ARCHIVE)

        if Params.FILTER_STARRED in self.params:
            self._put_bool_param(
                    api_params, Params.FILTER_STARRED, ApiParams.STARRED)

        if Params.TAGS in self.params:
            api_params[ApiParams.TAGS.value] = self.params[Params.TAGS]

        return api_params

    def __get_count(self, count):
        return 0 if not count or count < 0 else count
