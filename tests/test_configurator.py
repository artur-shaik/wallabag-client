# -*- coding: utf-8 -*-

import pytest

from wallabag import api
from wallabag.config import Options, Sections
from wallabag.configurator import (
        ClientOption, PasswordOption, SecretOption,
        ServerurlOption, UsernameOption)


class TestConfigurator():

    @pytest.mark.parametrize(
            'values',
            [('wb.site', 'https://wb.site'),
             ('http://wb.site/', 'http://wb.site'),
             ('https://wb.site', 'https://wb.site')])
    def test_serverurl_option(self, monkeypatch, values):
        def testresponse(self):
            return False

        def is_minimum_version(response):
            return True

        monkeypatch.setattr(api.Response, 'has_error', testresponse)
        monkeypatch.setattr(api, 'is_minimum_version', is_minimum_version)

        so = ServerurlOption()
        so.check_and_apply(values[0])

        assert values[1] == so.get_value()

    @pytest.mark.parametrize(
            'values',
            [(ServerurlOption(), (Sections.API, Options.SERVERURL)),
             (UsernameOption(), (Sections.API, Options.USERNAME)),
             (PasswordOption(), (Sections.API, Options.PASSWORD)),
             (ClientOption(), (Sections.OAUTH2, Options.CLIENT)),
             (SecretOption(), (Sections.OAUTH2, Options.SECRET))])
    def test_option_names(self, values):
        assert (values[1][0], values[1][1]) == values[0].get_option_name()
