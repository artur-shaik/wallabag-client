# -*- coding: utf-8 -*-


from wallabag.api.api import Api, ApiMethod
from wallabag.config import Options, Sections


class ApiToken(Api):

    def __init__(self, config):
        Api.__init__(self, config)
        self.skip_auth = True

    def _get_api_url(self):
        return self._build_url(ApiMethod.TOKEN)

    def _make_request(self, request):
        return self._request_get(request)

    def _get_params(self):
        return {
            'grant_type': "password",
            'client_id': self.config.get(Sections.OAUTH2, Options.CLIENT),
            'client_secret': self.config.get(Sections.OAUTH2, Options.SECRET),
            'username': self.config.get(Sections.API, Options.USERNAME),
            'password': self.config.get(Sections.API, Options.PASSWORD)
        }
