# -*- coding: utf-8 -*-

from .export import Export
from bs4 import BeautifulSoup

from colorama import Back, Fore

from lxml import etree


class ExportCli(Export):

    def __init__(self, entry, params, width):
        Export.__init__(self, entry)
        self.params = params
        self.width = width

    def run(self):
        soup = self.__mark_annotations(self.entry.content)
        self.__color_headers(soup)
        self.__color_bold(soup)
        self.__make_hr(soup)
        self.__replace_images(soup)
        self.__break_paragraphs(soup)
        result = self.__make_annotations(soup).replace('\n\n\n', '\n\n')
        return self.__output(self.entry.title, result)

    def __output(self, title, article):
        return (f"{title}\n"
                f"{self.__header_delimiter()}\n"
                f"{article}")

    def __header_delimiter(self):
        try:
            return "".ljust(self.width, '=')
        except OSError:
            return "\n"

    def __break_paragraphs(self, soup):
        for p in soup.findAll('p'):
            p.insert_before(self.__get_new_line_tag(soup, times=2))

    def __mark_annotations(self, html):
        soup = BeautifulSoup(html, "html.parser")
        if self.entry.annotations:
            dom = etree.HTML(str(soup))
            for anno in self.entry.annotations:
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

    def __make_annotations(self, soup):
        text = soup.text
        for anno in self.entry.annotations:
            anno_id = f"__anno-{anno['id']}__"
            text = text.replace(
                    f'{anno_id}_start', Back.CYAN).replace(
                            f'{anno_id}_end', f'{Back.RESET} [{anno["id"]}]')
        return text

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
