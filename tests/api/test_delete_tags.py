# -*- coding: utf-8 -*-

import pytest

from wallabag.api.api import ApiMethod, ValueException
from wallabag.api.delete_tag_from_entry import DeleteTagFromEntry
from wallabag.api.delete_tag_by_id import DeleteTagsById
from wallabag.api.delete_tags_by_label import DeleteTagsByLabel
from wallabag.config import Configs


class TestDeleteTags():

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

    def test_delete_from_entry_url(self):
        entry_id = 1
        tag_id = '2'
        api = DeleteTagFromEntry(self.config, entry_id, tag_id)
        url = 'url' + ApiMethod.DELETE_TAG_FROM_ENTRY.value.format(
                entry_id, tag_id)
        assert url == api._get_api_url()

    def test_delete_by_label(self):
        tag = 'tag'
        api = DeleteTagsByLabel(self.config, tag)
        url = 'url' + ApiMethod.DELETE_TAG_BY_LABEL.value
        assert url == api._get_api_url()
        assert DeleteTagsByLabel.ApiParams.TAGS.value in api._get_params()
        assert tag == api._get_params()[DeleteTagsByLabel.ApiParams.TAGS.value]

    def test_delete_by_id(self):
        tag_id = '10'
        api = DeleteTagsById(self.config, tag_id)
        url = 'url' + ApiMethod.DELETE_TAG_BY_ID.value.format(tag_id)
        assert url == api._get_api_url()

    @pytest.mark.parametrize('entry_id', ["-10", -10, None, "none"])
    def test_wrong_args(self, entry_id):
        api = DeleteTagFromEntry(self, entry_id, '10')
        with pytest.raises(ValueException):
            api._get_api_url()
