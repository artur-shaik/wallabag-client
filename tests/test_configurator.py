# -*- coding: utf-8 -*-

import os
import tempfile

import pytest

from wallabag.api import Api, Response
from wallabag.config import Configs, Options, Sections
from wallabag.configurator import (
        ClientOption, PasswordOption, SecretOption,
        ServerurlOption, UsernameOption, Validator)


def is_minimum_version(self, response):
    return True


def api_success(self):
    return Response(200, None)


def api_failure(self):
    return Response(403, None)


class TestConfigurator():

    fd = None

    def teardown_method(self, method):
        if self.fd:
            os.close(self.fd)
            os.remove(self.path)

    def setup_method(self, method):
        self.fd, self.path = tempfile.mkstemp()
        with open(self.path, 'w') as f:
            f.write('')
        self.configs = Configs(self.path)
        self.configs.config.read_string("""
                [api]
                serverurl = url
                username = user
                password = pass
                [oauth2]
                client = 100
                secret = 100
                """)

    @pytest.mark.parametrize(
            'values',
            [('wb.site', 'https://wb.site'),
             ('http://wb.site/', 'http://wb.site'),
             ('https://wb.site', 'https://wb.site')])
    def test_serverurl_option(self, monkeypatch, values):
        def testresponse(self):
            return False

        monkeypatch.setattr(Response, 'has_error', testresponse)
        monkeypatch.setattr(Api, 'is_minimum_version', is_minimum_version)

        so = ServerurlOption(Api(self.configs))
        so.check_and_apply(values[0])

        assert values[1] == so.get_value()

    @pytest.mark.parametrize(
            'values',
            [(ServerurlOption(Api), (Sections.API, Options.SERVERURL)),
             (UsernameOption(), (Sections.API, Options.USERNAME)),
             (PasswordOption(), (Sections.API, Options.PASSWORD)),
             (ClientOption(), (Sections.OAUTH2, Options.CLIENT)),
             (SecretOption(), (Sections.OAUTH2, Options.SECRET))])
    def test_option_names(self, values):
        assert (values[1][0], values[1][1]) == values[0].get_option_name()

    def test_validator_check_success(self, monkeypatch):
        monkeypatch.setattr(Api, 'api_version', api_success)
        monkeypatch.setattr(Api, 'api_token', api_success)
        monkeypatch.setattr(Api, 'is_minimum_version', is_minimum_version)

        (result, msg) = Validator(self.configs).check()

        assert result
        assert msg == 'The config is suitable.'

    def test_validator_check_error(self, monkeypatch):
        monkeypatch.setattr(Api, 'api_version', api_failure)
        monkeypatch.setattr(Api, 'api_token', api_failure)
        monkeypatch.setattr(Api, 'is_minimum_version', is_minimum_version)

        (result, msg) = Validator(self.configs).check()

        assert not result
        assert msg == 'The server or the API is not reachable.'

    def test_validator_oauth_success(self, monkeypatch):
        monkeypatch.setattr(Api, 'api_token', api_success)

        (result, msg, opts) = Validator(None).check_oauth()
        assert result
        assert msg == 'The configuration is ok.'

    def test_validator_oauth_failure(self, monkeypatch):
        monkeypatch.setattr(Api, 'api_token', api_failure)

        (result, msg, opts) = Validator(None).check_oauth()
        assert not result
        assert not msg

    def test_validator_oauth_failure_bad_request_grant(self, monkeypatch):
        def api_failure_400_grant(self):
            return Response(400, '{"error": "invalid_grant"}')

        monkeypatch.setattr(Api, 'api_token', api_failure_400_grant)

        (result, msg, options) = Validator(None).check_oauth()
        assert not result
        assert not msg
        assert len(options) == 2
        assert isinstance(options[0], UsernameOption)
        assert isinstance(options[1], PasswordOption)

    def test_validator_oauth_failure_bad_request_client(self, monkeypatch):
        def api_failure_400_client(self):
            return Response(400, '{"error": "invalid_client"}')

        monkeypatch.setattr(Api, 'api_token', api_failure_400_client)

        (result, msg, options) = Validator(None).check_oauth()
        assert not result
        assert not msg
        assert len(options) == 2
        assert isinstance(options[0], ClientOption)
        assert isinstance(options[1], SecretOption)
