# -*- coding: utf-8 -*-

import pytest

from wallabag.api.api import ApiMethod
from wallabag.api.get_list_entries import GetListEntries, Params
from wallabag.config import Configs


class TestGetEntriesList():

    def setup_method(self, method):
        self.config = Configs("/tmp/config")
        self.config.config.read_string("""
                [api]
                serverurl = url
                username = user
                password = pass
                [oauth2]
                client = 100
                secret = 100
                """)

    def test_api_url(self):
        api = GetListEntries(self.config, {
            Params.COUNT: 10
        })

        assert "url" + ApiMethod.LIST_ENTRIES.value == api._get_api_url()

    @pytest.mark.parametrize('count', [
        (10, 10), (None, 0), (-10, 0)
        ])
    def test_params_count(self, count):
        api = GetListEntries(self.config, {
            Params.COUNT: count[0]
        })

        params = api._get_params()
        assert GetListEntries.ApiParams.PER_PAGE.value in params
        assert params.get(GetListEntries.ApiParams.PER_PAGE.value) == count[1]

    @pytest.mark.parametrize('values', [
        ((
            Params.FILTER_READ,
            GetListEntries.ApiParams.ARCHIVE
            ), True, 1),
        ((
            Params.FILTER_READ,
            GetListEntries.ApiParams.ARCHIVE
            ), None, None),
        ((
            Params.FILTER_READ,
            GetListEntries.ApiParams.ARCHIVE
            ), False, 0),
        ((
            Params.FILTER_READ,
            GetListEntries.ApiParams.ARCHIVE
            ), 'foo', None),
        ((
            Params.FILTER_STARRED,
            GetListEntries.ApiParams.STARRED
            ), True, 1),
        ((
            Params.FILTER_STARRED,
            GetListEntries.ApiParams.STARRED
            ), None, None),
        ((
            Params.FILTER_STARRED,
            GetListEntries.ApiParams.STARRED
            ), False, 0),
        ((
            Params.FILTER_STARRED,
            GetListEntries.ApiParams.STARRED
            ), 'foo', None),
        ((
            Params.TAGS,
            GetListEntries.ApiParams.TAGS
            ), 'tag1,tag2', 'tag1,tag2')
        ])
    def test_bool_params(self, values):
        api = GetListEntries(self.config, {
            Params.COUNT: 1,
            values[0][0]: values[1]
        })

        params = api._get_params()
        if values[2] is not None:
            assert values[0][1].value in params
            assert params.get(values[0][1].value) == values[2]
        else:
            assert values[0][1].value not in params

    @pytest.mark.parametrize('oldest', [
        (True, GetListEntries.ApiValues.ORDER.value.ASC.value),
        (None, None), (False, None)
        ])
    def test_param_oldest(self, oldest):
        api = GetListEntries(self.config, {
            Params.COUNT: 1,
            Params.OLDEST: oldest[0]
        })

        params = api._get_params()
        if oldest[1]:
            assert GetListEntries.ApiParams.ORDER.value in params
            assert oldest[1] == params.get(
                    GetListEntries.ApiParams.ORDER.value)
        else:
            assert GetListEntries.ApiParams.ORDER.value not in params
