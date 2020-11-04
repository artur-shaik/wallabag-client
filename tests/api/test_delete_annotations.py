# -*- coding: utf-8 -*-

import pytest

from wallabag.api.api import ApiMethod, ValueException
from wallabag.api.delete_annotation import DeleteAnnotation
from wallabag.config import Configs


class TestDeleteAnnotations():

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

    def test_url(self):
        anno_id = 1
        api = DeleteAnnotation(self.config, anno_id)
        url = 'url' + ApiMethod.DELETE_ANNOTATION.value.format(anno_id)
        assert url == api._get_api_url()

    @pytest.mark.parametrize('anno_id', ["-10", -10, None, "none"])
    def test_wrong_args(self, anno_id):
        api = DeleteAnnotation(self, anno_id)
        with pytest.raises(ValueException):
            api._get_api_url()
