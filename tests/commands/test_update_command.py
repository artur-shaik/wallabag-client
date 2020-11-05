# -*- coding: utf-8 -*-

import pytest

from wallabag.api.api import Api, Response, RequestException
from wallabag.api.get_entry import GetEntry
from wallabag.api.update_entry import UpdateEntry
from wallabag.commands.update import UpdateCommand, UpdateCommandParams
from wallabag.config import Configs


def get_authorization_header(self):
    return {'Authorization': "Bearer a1b2"}


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

        params = UpdateCommandParams()
        params.toggle_read = True
        result, output = UpdateCommand(self.config, 1, params).execute()
        assert not result
        assert output == "Error: 404: API was not found."

    def test_no_parameters_given(self):
        result, output = UpdateCommand(
                self.config, 1, UpdateCommandParams()).execute()
        assert not result
        assert output == 'No parameter given'

    @pytest.mark.parametrize('values', [
        ((0, 0), (1, 0), (True, False, None, None)),
        ((1, 0), (0, 0), (True, False, None, None)),
        ((0, 1), (0, 0), (False, True, None, None)),
        ((0, 0), (0, 1), (False, True, None, None)),
        ((0, 0), (1, 0), (None, None, True, None)),
        ((0, 0), (1, 0), (True, None, True, None)),
        ((0, 0), (0, 1), (None, None, None, True)),
        ((0, 1), (0, 1), (None, True, None, True)),
        ((0, 1), (0, 0), (None, None, False, None)),
        ((0, 0), (0, 0), (None, None, None, False)),
        ])
    def test_toggle_parameters(self, monkeypatch, values):
        make_request_runned = False

        def _make_request(self, request):
            nonlocal make_request_runned
            make_request_runned = True
            if values[1][0] == 1 or values[2][2] is not None:
                assert request.data[UpdateEntry.ApiParams.ARCHIVE.value]\
                        == values[1][0]
            if values[1][1] == 1 or values[2][3] is not None:
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
        monkeypatch.setattr(
                Api, '_get_authorization_header', get_authorization_header)

        params = UpdateCommandParams()
        params.toggle_read = values[2][0]
        params.toggle_star = values[2][1]
        params.set_read_state = values[2][2]
        params.set_star_state = values[2][3]
        result, output = UpdateCommand(self.config, 1, params).execute()
        assert result
        assert make_request_runned
