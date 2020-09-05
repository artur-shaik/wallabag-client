# -*- coding: utf-8 -*-

import re
from abc import ABC, abstractmethod

import click

from wallabag.config import Options, Sections

from . import api


class Configurator():

    def __init__(self, config):
        self.config = config

    def start(self, options=[]):
        if not options:
            options = ConfigOption.get_all()
        for option in options:
            (sec, opt) = option.get_option_name()
            option.set_default(self.config.get(sec, opt))
            while True:
                value = click.prompt(option.get_prompt(),
                                     default=option.get_default())
                try:
                    option.check_and_apply(value)
                    self.config.set_config(
                            sec, opt, option.get_value())
                    break
                except ValueError as e:
                    click.echo(e)

        self.config.save()
        self._check_oauth()

    def check(self):
        if not self.config.is_valid():
            raise ValueError("The config is missing or incomplete.")

        response = api.api_version()
        if response.has_error():
            raise ValueError("The server or the API is not reachable.")

        if not api.is_minimum_version(response):
            raise ValueError(
                    "The version of the wallabag instance is too old.")

        response = api.api_token()
        if response.has_error():
            raise ValueError(response.error_description)

        click.echo("The config is suitable.")

    def _check_oauth(self):
        testresponse = api.api_token()
        if testresponse.has_error():
            self.config.save()
            if testresponse.error == api.Error.http_bad_request:
                click.echo(testresponse.error_description)
                if testresponse.error_text == "invalid_grant":
                    self.start([UsernameOption(), PasswordOption()])
                    return
                elif testresponse.error_text == "invalid_client":
                    self.start([ClientOption(), SecretOption()])
                    return
            raise ValueError(testresponse.error_description)

        self.config.save()
        click.echo("The config was saved successfully.")


class ConfigOption(ABC):

    prompt = ''
    default = ''

    def get_all():
        return [ServerurlOption(), UsernameOption(), PasswordOption(),
                ClientOption(), SecretOption()]

    def __init__(self, default=None):
        self.set_default(default)

    def get_prompt(self):
        return self.prompt

    def get_default(self):
        return self.default

    def set_default(self, default):
        if default:
            self.default = default

    def check_and_apply(self, value):
        value = value.strip()

        if not value:
            if self.get_default():
                value = self.get_default()
            else:
                raise ValueError("Empty value")

        self.value = value

    @abstractmethod
    def get_option_name(self):
        pass

    def get_value(self):
        return self.value


class ServerurlOption(ConfigOption):

    RE_HTTP = re.compile("(?i)https?:\\/\\/.+")

    prompt = 'Enter the url of your Wallabag instance'
    default = 'https://www.wallabag.com/'

    def check_and_apply(self, value):
        value = value.strip()

        if not value:
            value = self.get_default()

        if value[-1] == '/':
            value = value[:-1]

        if not ServerurlOption.RE_HTTP.match(value):
            value = "https://" + value

        testresponse = api.api_version(value)
        if testresponse.has_error():
            raise ValueError(testresponse.error_text)

        if not api.is_minimum_version(testresponse):
            raise ValueError(
                    "Your wallabag instance is too old. \
                            You need at least version \
                            {api.MINIMUM_API_VERSION_HR}.")

        self.value = value

    def get_option_name(self):
        return (Sections.API, Options.SERVERURL)


class UsernameOption(ConfigOption):

    prompt = 'Enter your Wallabag username'

    def get_option_name(self):
        return (Sections.API, Options.USERNAME)


class PasswordOption(ConfigOption):

    prompt = 'Enter your Wallabag password'

    def get_option_name(self):
        return (Sections.API, Options.PASSWORD)


class ClientOption(ConfigOption):

    prompt = 'Enter the client id of your Wallabag API'

    def get_option_name(self):
        return (Sections.OAUTH2, Options.CLIENT)


class SecretOption(ConfigOption):

    prompt = 'Enter the client secret of your Wallabag API'

    def get_option_name(self):
        return (Sections.OAUTH2, Options.SECRET)
