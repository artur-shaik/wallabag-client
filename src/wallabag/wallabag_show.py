"""
Show a wallabag entry
"""
import io
import formatter
import json
import os
from sys import exit
import sys
from bs4 import BeautifulSoup

from . import api
from . import conf
from . import entry


def show(entry_id, colors=True, raw=False, html=False):
    """
    Main function for showing an entry.
    """
    conf.load()
    try:
        request = api.api_get_entry(entry_id)
        __handle_request_error(request)
        entr = entry.Entry(json.loads(request.response))
    except api.OAuthException as ex:
        print("Error: {0}".format(ex.text))
        print()
        exit(-1)

    title = entr.title

    try:
        delimiter = "".ljust(os.get_terminal_size().columns, '=')
    # piped output to file or other process
    except OSError:
        delimiter = "\n"
        
    article = entr.content
    if not html:
        article = html2text(article, colors)

    output = "{0}\n{1}\n{2}".format(title, delimiter, article)

    if not raw:
        output = __format_text(output)

    print(output)


def html2text(html, colors=True):
    soup = BeautifulSoup(html, "html.parser")

    # Color h1-h3
    if colors:
        h1colors = '\033[93m'
        h1colore = '\033[0m'
    else:
        h1colors = h1colore = ""
    for h1 in soup.findAll('h1'):
        h1.string = "\n{0}{1}{2}".format(h1colors, h1.string, h1colore)
    for h2 in soup.findAll('h2'):
        h2.string = "\n{0}{1}{2}".format(h1colors, h2.string, h1colore)
    for h3 in soup.findAll('h3'):
        h3.string = "\n{0}{1}{2}".format(h1colors, h3.string, h1colore)

    if colors:
        # Color bold texts
        bcolors = '\033[92m'
        bcolore = '\033[0m'
        for bold in soup.findAll('b'):
            bold.string = "{0}{1}{2}".format(bcolors, bold.string, bcolore)
        for bold in soup.findAll('strong'):
            bold.string = "{0}{1}{2}".format(bcolors, bold.string, bcolore)

    # Replace hr with visual lines
    try:
        hrstring = "".ljust(os.get_terminal_size().columns, '-')
    # piped output to file or other process
    except OSError:
        hrstring = "-----"
    for hr in soup.findAll('hr'):
        replace = soup.new_tag('p')
        replace.string = hrstring
        hr.insert_after(replace)
        hr.unwrap()

    # Replace images by information-texts
    for img in soup.findAll('img'):
        replace = soup.new_tag('p')
        try:
            alt = " \"{0}\"".format(img['alt'])
        except KeyError:
            alt = ""
        replace.string = "[IMAGE{0}]\n".format(alt)
        img.insert_after(replace)
        img.unwrap()

    return soup.text


def __format_text(text):
    try:
        maxcol = os.get_terminal_size().columns
    # piped output to file or other process
    except OSError:
        maxcol = sys.maxsize

    ret = ""

    for line in text.splitlines():
        ios = io.StringIO()
        writer = formatter.DumbWriter(ios, maxcol=maxcol)
        writer.send_flowing_data(line)
        ret = "{0}{1}\n".format(ret, ios.getvalue())
        ios.close()

    return ret


def __handle_request_error(request):
    if request.has_error():
        if request.error == api.Error.http_forbidden or request.error == api.Error.http_not_found:
            print("Error: Invalid entry id.")
            print()
            exit(-1)
        print("Error: {0} - {1}".format(request.error_text,
                                        request.error_description))
        exit(-1)
