# -*- coding: utf-8 -*-

import webbrowser

from wallabag.commands.command import Command
from wallabag.commands.params import Params
from wallabag.api.get_entry import GetEntry
from wallabag.entry import Entry
from wallabag.config import Sections, Options


class OpenCommandParams(Params):
    entry_id = None
    open_original = False
    browser = None

    def __init__(self, entry_id, open_original=False, browser=None):
        self.entry_id = entry_id
        self.open_original = open_original
        self.browser = browser

    def validate(self):
        if not self.entry_id:
            return False, 'Entry ID not specified'
        return True, None


class OpenCommand(Command):

    def __init__(self, config, params):
        Command.__init__(self)
        self.config = config
        self.params = params if params else OpenCommandParams(None)

    def _run(self):
        api = GetEntry(self.config, self.params.entry_id)
        entry = Entry(api.request().response)

        url = ""
        if self.params.open_original:
            url = entry.url
        else:
            serverurl = self.config.get(Sections.API, Options.SERVERURL)
            url = f"{serverurl}/view/{entry.entry_id}"

        browser = webbrowser.get(self.params.browser)
        browser.open_new_tab(url)

        return True, None
