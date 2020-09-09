#!/usr/bin/env python

from enum import Enum

from wallabag.api.api import Api, ApiMethod


class GetListEntries(Api):

    API_METHOD = ApiMethod.LIST_ENTRIES

    class Params(Enum):
        COUNT = "count"
        FILTER_READ = "filter_read"
        FILTER_STARRED = "filter_starred"
        OLDEST = "oldest"

    class ApiParams(Enum):
        PER_PAGE = "perPage"
        OLDEST = "oldest"
        ARCHIVE = "archive"
        STARRED = "starred"

    class ApiValues(Enum):
        class OLDEST(Enum):
            ASC = "asc"

    def __init__(self, config, params):
        Api.__init__(self, config)
        self.params = params

    def _make_request(self):
        return self._request_get()

    def _get_api_url(self):
        return self._build_url(GetListEntries.API_METHOD)

    def _get_params(self):
        Params = self.Params
        ApiParams = self.ApiParams
        ApiValues = self.ApiValues
        api_params = {
            ApiParams.PER_PAGE: self.__get_count(self.params[Params.COUNT])
        }

        if Params.OLDEST in self.params and self.params[Params.OLDEST]:
            api_params[ApiParams.OLDEST] = ApiValues.OLDEST.value.ASC

        if Params.FILTER_READ in self.params:
            self.__put_bool_param(
                    api_params, Params.FILTER_READ, ApiParams.ARCHIVE)

        if Params.FILTER_STARRED in self.params:
            self.__put_bool_param(
                    api_params, Params.FILTER_STARRED, ApiParams.STARRED)

        return api_params

    def __get_count(self, count):
        return 0 if not count or count < 0 else count

    def __put_bool_param(self, api_params, param, api_param):
        if self.params[param] is not None:
            if isinstance(self.params[param], bool):
                api_params[api_param] = 1 if self.params[param] else 0
