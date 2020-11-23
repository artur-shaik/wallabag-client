# -*- coding: utf-8 -*-

import os
import textwrap
from enum import Enum, auto
from bs4 import BeautifulSoup
from colorama import Fore, Back
from lxml import etree

from wallabag.api.get_entry import GetEntry
from wallabag.commands.command import Command
from wallabag.commands.params import Params
from wallabag.entry import Entry


class Alignment(Enum):
    CENTER = auto()
    LEFT = auto()
    RIGHT = auto()

    def list():
        return [c.name for c in Alignment]

    def get(name):
        for align in Alignment:
            if align.name == name.upper():
                return align
        return Alignment.CENTER


class ShowCommandParams(Params):
    width = '80%'
    align = Alignment.CENTER

    def __init__(self, entry_id, colors=True, html=False,
                 raw=False, image_links=False):
        self.entry_id = entry_id
        self.colors = colors
        self.html = html
        self.raw = raw
        self.image_links = image_links


class ShowCommand(Command):

    FAILWIDTH = 100

    def __init__(self, config, params):
        Command.__init__(self)
        self.config = config
        self.params = params

    def _run(self):
        api = GetEntry(self.config, self.params.entry_id)
        entry = Entry(api.request().response)

        self.__calculate_alignment()

        article = entry.content
        if not self.params.html:
            article = self.__html2text(article, entry.annotations)

        output = f"{entry.title}\n{self.__header_delimiter()}\n{article}"
        if not self.params.raw:
            output = self.__format_output(output)
        return True, output

    def __calculate_alignment(self):
        try:
            self.maxcol = os.get_terminal_size().columns
        except OSError:
            self.maxcol = ShowCommand.FAILWIDTH

        self.width = self.maxcol
        if self.params.width:
            if '%' in self.params.width:
                percent = int(self.params.width[:-1])
                self.width = int(self.width * percent / 100)
            else:
                self.width = int(self.params.width)
                if self.width > self.maxcol:
                    self.width = self.maxcol

    def __format_output(self, output):
        result = []
        for line in output.splitlines():
            result.extend(textwrap.wrap(line, self.width) if line else [''])
        result = textwrap.indent(
                "\n".join(result), ' ' * self.__indent(self.params.align))
        return result

    def __indent(self, align):
        if align == Alignment.CENTER:
            return int((self.maxcol - self.width) / 2)
        elif align == Alignment.RIGHT:
            return self.maxcol - self.width
        return 0

    def __html2text(self, html, annotations):
        soup = self.__mark_annotations(html, annotations)
        self.__color_headers(soup)
        self.__color_bold(soup)
        self.__make_hr(soup)
        self.__replace_images(soup)
        self.__break_paragraphs(soup)
        return self.__make_annotations(
                soup, annotations).replace('\n\n\n', '\n\n')

    def __break_paragraphs(self, soup):
        for p in soup.findAll('p'):
            p.insert_before(self.__get_new_line_tag(soup, times=2))

    def __mark_annotations(self, html, annotations):
        soup = BeautifulSoup(html, "html.parser")
        if annotations:
            dom = etree.HTML(str(soup))
            for anno in annotations:
                anno_id = f"__anno-{anno['id']}__"
                startOffset = int(anno['ranges'][0]['startOffset'])
                endOffset = int(anno['ranges'][0]['endOffset'])
                el_start = dom.xpath('/' + anno['ranges'][0]['start'])[0]
                el_end = dom.xpath('/' + anno['ranges'][0]['end'])[0]
                el_start.text = "".join([
                        el_start.text[:startOffset],
                        f'{anno_id}_start',
                        el_start.text[startOffset:]])
                if el_start == el_end:
                    endOffset += len(f'{anno_id}_start')
                el_end.text = "".join([
                        el_end.text[:endOffset],
                        f'{anno_id}_end',
                        el_end.text[endOffset:]])
            return BeautifulSoup(
                    etree.tostring(dom, method='html'), "html.parser")
        return soup

    def __make_annotations(self, soup, annotations):
        text = soup.text
        for anno in annotations:
            anno_id = f"__anno-{anno['id']}__"
            text = text.replace(
                    f'{anno_id}_start', Back.CYAN).replace(
                            f'{anno_id}_end', f'{Back.RESET} [{anno["id"]}]')
        return text

    def __header_delimiter(self):
        try:
            return "".ljust(self.width, '=')
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
        span = soup.new_tag('span')
        span.string = "\n" * times
        return span

    def __color_bold(self, soup):
        if self.params.colors:
            bcolors = Fore.RED
            bcolore = Fore.RESET
            for bold in ['b', 'strong']:
                for b in soup.findAll('b'):
                    b.string = f"{bcolors}{b.string}{bcolore}"

    def __make_hr(self, soup):
        try:
            print(self.width)
            hrstring = "".ljust(self.width, '-')
        except OSError:
            hrstring = "-----"
        for hr in soup.findAll('hr'):
            replace = soup.new_tag('p')
            replace.string = hrstring
            hr.insert_after(replace)
            hr.unwrap()

    def __replace_images(self, soup):
        for img in soup.findAll('img'):
            replace = soup.new_tag('span')
            try:
                alt = f" \"{img['alt']}\""
            except KeyError:
                alt = ""
            links = ""
            if self.params.image_links:
                links = f" ({img['src']})"
            replace.string = f" [IMAGE{alt}{links}]\n"
            img.insert_after(replace)
            img.unwrap()
