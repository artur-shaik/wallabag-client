# -*- coding: utf-8 -*-

import logging
import re
import time
from abc import ABC, abstractmethod

from wallabag.api.api import (
        Api, Error, MINIMUM_API_VERSION, RequestException)
from wallabag.api.get_api_version import ApiVersion
from wallabag.api.api_token import ApiToken
from wallabag.commands.command import Command
from wallabag.config import Options, Sections
from wallabag import wclick


class Configurator():

    def __init__(self, config):
        self.log = logging.getLogger('wallabag.config')
        self.config = config

    def start(self, options=[]):
        if not options:
            options = ConfigOption.get_all(self.config)
        for option in options:
            self.log.debug('configuring: %s', option.__class__.__name__)

            while not option.setup(self.config):
                pass

        self.config.save()


class Validator(Command):

    def __init__(self, config):
        Command.__init__(self)
        self.config = config
        self.response = {
            'invalid_grant': (
                False, None, [UsernameOption(), PasswordOption()]),
            'invalid_client': (
                False, None, [ClientOption(), SecretOption()])
        }

    def check_oauth(self):
        try:
            ApiToken(self.config).request()
        except RequestException as error:
            response = error.response
            if response and response.error == Error.HTTP_BAD_REQUEST:
                wclick.echo(response.error_description)
                return self.response[response.error_text]
            return (False, error.error_description, None)
        return (True, "The configuration is ok.", None)

    def _run(self):
        if not self.config.is_valid():
            return False, "The config is missing or incomplete."

        try:
            response = ApiVersion(self.config).request()
        except RequestException:
            return False, "The server or the API is not reachable."

        if not Api.is_minimum_version(response):
            return False, "The version of the wallabag instance is too old."

        ApiToken(self.config).request()

        return True, "The config is suitable."


class ConfigOption(ABC):

    prompt = ''
    default = ''

    def get_all(config):
        return [ServerurlOption(config), UsernameOption(),
                PasswordOption(), ClientOption(), SecretOption()]

    def __init__(self, default=None):
        self.set_default(default)

    def _check_existence_or_default(self, value):
        if not value:
            if not self.get_default():
                raise ValueError("Empty value")
            return self.get_default()
        return value

    def get_prompt(self):
        return self.prompt

    def get_default(self):
        return self.default

    def set_default(self, default):
        if default:
            self.default = default

    @abstractmethod
    def get_option_name(self):
        pass

    def check_and_apply(self, value):
        self.value = self._check_existence_or_default(value.strip())

    def get_value(self):
        return self.value

    def setup(self, config):
        (sec, opt) = self.get_option_name()
        self.set_default(config.get(sec, opt))
        value = wclick.prompt(self.get_prompt(),
                              default=self.get_default())
        try:
            self.check_and_apply(value)
        except ValueError as e:
            wclick.echo(e)
            return False
        config.set(sec, opt, self.get_value())
        return True


class ServerurlOption(ConfigOption):

    RE_HTTP = re.compile("(?i)https?:\\/\\/.+")

    prompt = 'Enter the url of your Wallabag instance'
    default = 'https://www.wallabag.com/'

    def __init__(self, config):
        self.config = config

    def __check_trailing_space(self, value):
        return value[:-1] if value[-1] == '/' else value

    def __check_https(self, value):
        return f"https://{value}" if not ServerurlOption.RE_HTTP.match(value)\
                else value

    def __check_api_verion(self, value):
        try:
            response = ApiVersion(self.config, value).request()
        except RequestException as err:
            raise ValueError(str(err))

        if not Api.is_minimum_version(response):
            raise ValueError(
                    f"Your wallabag instance is too old. \
                            You need at least version \
                            {MINIMUM_API_VERSION}.")

    def check_and_apply(self, value):
        value = self._check_existence_or_default(value.strip())
        value = self.__check_trailing_space(value)
        value = self.__check_https(value)
        self.__check_api_verion(value)
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


class TokenConfigurator():

    def __init__(self, config):
        self.config = config

    def get_token(self, force_creation=False):
        if self.config.is_token_expired() or force_creation:
            response = ApiToken(self.config).request()
            content = response.response
            self.config.set(
                    Sections.TOKEN,
                    Options.ACCESS_TOKEN,
                    content['access_token'])
            self.config.set(
                    Sections.TOKEN,
                    Options.EXPIRES,
                    str(time.time() + content['expires_in']))
            self.config.save()
            return self.config.get(
                    Sections.TOKEN,
                    Options.ACCESS_TOKEN)
        else:
            return self.config.get(
                    Sections.TOKEN,
                    Options.ACCESS_TOKEN)
