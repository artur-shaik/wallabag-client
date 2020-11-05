# -*- coding: utf-8 -*-

import os
import tempfile

import pytest

from wallabag.api.api import Api, Response, RequestException
from wallabag.api.get_api_version import ApiVersion
from wallabag.api.api_token import ApiToken
from wallabag.config import Configs, Options, Sections
from wallabag.configurator import (
        ClientOption, Configurator, PasswordOption, SecretOption,
        ServerurlOption, UsernameOption, Validator)


def is_minimum_version(response):
    return True


def api_success(self):
    return Response(200, None)


def api_failure(self):
    raise RequestException(response=Response(403, None))


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

    def test_init_configurator(self):
        c = Configurator(self.configs)
        assert c.config == self.configs

    def test_option_pass(self, monkeypatch):
        setup_runned = False

        def setup(self, config):
            nonlocal setup_runned
            setup_runned = True
            return True

        def save(self):
            pass

        monkeypatch.setattr(UsernameOption, 'setup', setup)
        monkeypatch.setattr(Configs, 'save', save)

        c = Configurator(self.configs)
        c.start([UsernameOption()])
        assert setup_runned

    @pytest.mark.parametrize(
            'values',
            [('wb.site', 'https://wb.site'),
             ('http://wb.site/', 'http://wb.site'),
             ('https://wb.site', 'https://wb.site')])
    def test_serverurl_option(self, monkeypatch, values):
        def testresponse(self):
            return False

        monkeypatch.setattr(Response, 'has_error', testresponse)
        monkeypatch.setattr(ApiVersion, 'request', api_success)
        monkeypatch.setattr(Api, 'is_minimum_version', is_minimum_version)

        so = ServerurlOption(self.configs)
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
        monkeypatch.setattr(ApiVersion, 'request', api_success)
        monkeypatch.setattr(ApiToken, 'request', api_success)
        monkeypatch.setattr(Api, 'is_minimum_version', is_minimum_version)

        (result, msg) = Validator(self.configs).execute()

        assert result
        assert msg == 'The config is suitable.'

    def test_validator_check_error(self, monkeypatch):
        monkeypatch.setattr(ApiVersion, 'request', api_failure)
        monkeypatch.setattr(ApiToken, 'request', api_failure)
        monkeypatch.setattr(Api, 'is_minimum_version', is_minimum_version)

        (result, msg) = Validator(self.configs).execute()

        assert not result
        assert msg == 'The server or the API is not reachable.'

    def test_validator_oauth_success(self, monkeypatch):
        monkeypatch.setattr(ApiToken, 'request', api_success)

        (result, msg, opts) = Validator(None).check_oauth()
        assert result
        assert msg == 'The configuration is ok.'

    def test_validator_oauth_failure(self, monkeypatch):
        monkeypatch.setattr(ApiToken, 'request', api_failure)

        (result, msg, opts) = Validator(None).check_oauth()
        assert not result
        assert not msg

    def test_validator_oauth_failure_bad_request_grant(self, monkeypatch):
        def api_failure_400_grant(self):
            raise RequestException(
                    response=Response(400, '{"error": "invalid_grant"}'))

        monkeypatch.setattr(ApiToken, 'request', api_failure_400_grant)

        (result, msg, options) = Validator(None).check_oauth()
        assert not result
        assert not msg
        assert len(options) == 2
        assert isinstance(options[0], UsernameOption)
        assert isinstance(options[1], PasswordOption)

    def test_validator_oauth_failure_bad_request_client(self, monkeypatch):
        def api_failure_400_client(self):
            raise RequestException(
                    response=Response(400, '{"error": "invalid_client"}'))

        monkeypatch.setattr(ApiToken, 'request', api_failure_400_client)

        (result, msg, options) = Validator(None).check_oauth()
        assert not result
        assert not msg
        assert len(options) == 2
        assert isinstance(options[0], ClientOption)
        assert isinstance(options[1], SecretOption)
