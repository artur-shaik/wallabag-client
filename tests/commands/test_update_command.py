# -*- coding: utf-8 -*-

import pytest

from wallabag.api.api import Response, RequestException
from wallabag.api.get_entry import GetEntry
from wallabag.api.update_entry import UpdateEntry
from wallabag.commands.update import UpdateCommand, UpdateCommandParams
from wallabag.config import Configs


class TestUpdateCommand():

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

    def test_not_existed_entry(self, monkeypatch):
        def request(self):
            response = Response(404, None)
            raise RequestException(
                    response.error_text, response.error_description)

        monkeypatch.setattr(GetEntry, 'request', request)

        params = UpdateCommandParams(1)
        params.toggle_read = True
        result, output = UpdateCommand(self.config, params).run()
        assert not result
        assert output == "Error: 404: API was not found."

    def test_no_parameters_given(self):
        result, output = UpdateCommand(
                self.config, UpdateCommandParams(1)).run()
        assert not result
        assert output == 'Error: No parameter given.'

    @pytest.mark.parametrize('values', [
        ((0, 0), (1, 0), (True, False)),
        ((1, 0), (0, 0), (True, False)),
        ((0, 1), (0, 0), (False, True)),
        ((0, 0), (0, 1), (False, True)),
        ])
    def test_toggle_parameters(self, monkeypatch, values):
        make_request_runned = False

        def _make_request(self, request):
            nonlocal make_request_runned
            make_request_runned = True
            if values[1][0] == 1:
                assert request.data[UpdateEntry.ApiParams.ARCHIVE.value]\
                        == values[1][0]
            if values[1][1] == 1:
                assert request.data[UpdateEntry.ApiParams.STARRED.value]\
                        == values[1][1]
            return Response(200)

        def request(self):
            return Response(
                    200, '{"id": 1, "title": "title", "content": "content",\
                            "url": "url", "is_archived": %s, "is_starred": %s}'
                    % (values[0][0], values[0][1]))

        monkeypatch.setattr(GetEntry, 'request', request)
        monkeypatch.setattr(UpdateEntry, '_make_request', _make_request)

        params = UpdateCommandParams(1)
        params.toggle_read = values[2][0]
        params.toggle_star = values[2][1]
        result, output = UpdateCommand(self.config, params).run()
        assert result
        assert make_request_runned
