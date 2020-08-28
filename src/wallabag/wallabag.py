#!/usr/bin/env python3
"""
The main entry point of wallabag-cli.
"""
import click
import functools
import platform
import subprocess
from sys import exit

from . import conf
from . import wallabag_add
from . import wallabag_config
from . import wallabag_delete
from . import wallabag_list
from . import wallabag_show
from . import wallabag_update


@click.group()
@click.option('--config', help='configuration file')
def cli(config):
    # Workaround for default non-unicode encodings in the
    # Windows cmd and Powershell
    # -> Analyze encoding and set to utf-8
    if platform.system() == "Windows":
        codepage = subprocess.check_output(['chcp'], shell=True).decode()
        if "65001" not in codepage:
            subprocess.check_output(['chcp', '65001'], shell=True)

    if config:
        conf.set_path(config)


def need_config(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not conf.is_valid():
            i = input(
                """Could not find a valid config.
Would you like to create it now? [Y/n]
""")
            if str.lower(i) in ["y", "yes", ""]:
                wallabag_config.start()
            else:
                exit(0)
        func(*args, **kwargs)

    return wrapper


@cli.command()
@click.option('-s/-u', '--starred/--unstarred', default=None)
@click.option('-r/-n', '--read/--unread', default=None)
@click.option('-a', '--all', default=False, is_flag=True)
@click.option('-o', '--oldest', default=False, is_flag=True)
@click.option('-t', '--trim-output', default=False, is_flag=True)
@click.option('-c', '--count', default=False, is_flag=True)
@click.option('-q', '--quantity', type=click.INT)
@need_config
def list(starred, read, all, oldest, trim_output, count, quantity):
    if all:
        read = None
        starred = None

    if count:
        wallabag_list.count_entries(read, starred)
    else:
        wallabag_list.list_entries(
            quantity, read, starred, oldest, trim_output)


@cli.command()
@click.option('-c/-n', '--color/--no-color', default=True)
@click.option('-r', '--raw', default=False, is_flag=True)
@click.option('-t', '--html', default=False, is_flag=True)
@click.argument('entry_id', required=True)
@need_config
def show(entry_id, color, raw, html):
    wallabag_show.show(entry_id, color, raw, html)


@cli.command()
@click.option('-q', '--quiet', default=False, is_flag=True)
@click.argument('entry_id', required=True)
@need_config
def read(entry_id, quiet):
    wallabag_update.update(entry_id, toggle_read=True, quiet=quiet)


@cli.command()
@click.option('-q', '--quiet', default=False, is_flag=True)
@click.argument('entry_id', required=True)
@need_config
def star(entry_id, quiet):
    wallabag_update.update(entry_id, toggle_star=True, quiet=quiet)


@cli.command()
@click.option('-t', '--title', default="")
@click.option('-r', '--read', default=False, is_flag=True)
@click.option('-s', '--starred', default=False, is_flag=True)
@click.option('-q', '--quiet', default=False, is_flag=True)
@click.argument('url', required=True)
@need_config
def add(url, title, read, starred, quiet):
    wallabag_add.add(url, title, starred, read, quiet)


@cli.command()
@click.option('-f', '--force', default=False, is_flag=True)
@click.option('-q', '--quiet', default=False, is_flag=True)
@click.argument('entry_id', required=True)
@need_config
def delete(entry_id, force, quiet):
    wallabag_delete.delete(entry_id, force, quiet)


@cli.command()
@click.option('-t', '--title', default="")
@click.option('-r', '--toggle-read', is_flag=True)
@click.option('-s', '--toggle-starred', is_flag=True)
@click.option('-q', '--quiet', is_flag=True)
@click.argument('entry_id', required=True)
@need_config
def update(entry_id, title, toggle_read, toggle_starred, quiet):
    if not title and not toggle_read and not toggle_starred:
        click.echo("Error: No parameter given.")
        exit(-1)
    wallabag_update.update(entry_id, toggle_read, toggle_starred, title, quiet)


@cli.command()
@click.option('-c', '--check', is_flag=True)
@click.option('-p', '--password', is_flag=True)
@click.option('-o', '--oauth', is_flag=True)
def config(check, password, oauth):
    if check:
        wallabag_config.check()
        exit(0)
    if password or oauth:
        if not conf.is_valid():
            click.echo(
                """Invalid existing config.
Therefore you have to enter all values.
                """)
            wallabag_config.start()
        else:
            wallabag_config.start(False, False, password, oauth)
    else:
        wallabag_config.start()
