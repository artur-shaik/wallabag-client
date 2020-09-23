# -*- coding: utf-8 -*-

import os
import sys
import textwrap
from bs4 import BeautifulSoup
from colorama import Fore

from wallabag.api.api import ApiException
from wallabag.api.get_entry import GetEntry
from wallabag.commands.command import Command
from wallabag.entry import Entry


class ShowCommandParams():

    def __init__(self, entry_id, colors=True, html=False,
                 raw=False, image_links=False):
        self.entry_id = entry_id
        self.colors = colors
        self.html = html
        self.raw = raw
        self.image_links = image_links


class ShowCommand(Command):

    def __init__(self, config, params):
        self.config = config
        self.params = params

    def run(self):
        try:
            api = GetEntry(self.config, self.params.entry_id)
            entry = Entry(api.request().response)
        except ApiException as ex:
            return False, str(ex)

        article = entry.content
        if not self.params.html:
            article = self.__html2text(article)

        output = f"{entry.title}\n{self.__header_delimiter()}\n{article}"
        if not self.params.raw:
            output = self.__format_output(output)
        return True, output

    def __format_output(self, output):
        try:
            maxcol = os.get_terminal_size().columns
        except OSError:
            maxcol = sys.maxsize

        result = []
        for line in output.splitlines():
            result.extend(textwrap.wrap(line, maxcol) if line else [''])
        return "\n".join(result)

    def __html2text(self, html):
        soup = BeautifulSoup(html, "html.parser")
        self.__color_headers(soup)
        self.__color_bold(soup)
        self.__make_hr(soup)
        self.__replace_images(soup)
        return soup.text

    def __header_delimiter(self):
        try:
            return "".ljust(os.get_terminal_size().columns, '=')
        except OSError:
            return "\n"

    def __color_headers(self, soup):
        if self.params.colors:
            h1colors = Fore.BLUE
            h1colore = Fore.RESET
        else:
            h1colors = h1colore = ""
        for header in ['h1', 'h2', 'h3']:
            for h in soup.findAll(header):
                h.string = f"{h1colors}{h.string}{h1colore}"
                h.insert_before(self.__get_new_line_tag(soup, 2))
                h.insert_after(self.__get_new_line_tag(soup))
                h.unwrap()

    def __get_new_line_tag(self, soup, times=1):
        p = soup.new_tag('p')
        p.string = "\n" * times
        return p

    def __color_bold(self, soup):
        if self.params.colors:
            bcolors = Fore.RED
            bcolore = Fore.RESET
            for bold in ['b', 'strong']:
                for b in soup.findAll('b'):
                    b.string = f"{bcolors}{b.string}{bcolore}"

    def __make_hr(self, soup):
        try:
            hrstring = "".ljust(os.get_terminal_size().columns, '-')
        except OSError:
            hrstring = "-----"
        for hr in soup.findAll('hr'):
            replace = soup.new_tag('p')
            replace.string = hrstring
            hr.insert_after(replace)
            hr.unwrap()

    def __replace_images(self, soup):
        for img in soup.findAll('img'):
            replace = soup.new_tag('p')
            try:
                alt = f" \"{img['alt']}\""
            except KeyError:
                alt = ""
            links = ""
            if self.params.image_links:
                links = f" ({img['src']})"
            replace.string = f"[IMAGE{alt}{links}]\n"
            img.insert_after(replace)
            img.unwrap()
