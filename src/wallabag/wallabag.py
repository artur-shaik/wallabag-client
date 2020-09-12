#!/usr/bin/env python3
"""
The main entry point of wallabag-cli.
"""
import functools
import platform
import subprocess
from sys import exit

import click

from wallabag.config import Configs
from wallabag.configurator import (
        ClientOption,
        Configurator,
        PasswordOption,
        SecretOption,
        Validator,
    )

from . import wallabag_add
from . import wallabag_delete
from . import wallabag_list
from . import wallabag_show
from . import wallabag_update


@click.group()
@click.option('--config', help='Use custom configuration file')
@click.pass_context
def cli(ctx, config):
    # Workaround for default non-unicode encodings in the
    # Windows cmd and Powershell
    # -> Analyze encoding and set to utf-8
    if platform.system() == "Windows":
        codepage = subprocess.check_output(['chcp'], shell=True).decode()
        if "65001" not in codepage:
            subprocess.check_output(['chcp', '65001'], shell=True)

    ctx.obj = Configs(config)


def need_config(func):
    @functools.wraps(func)
    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        if not ctx.obj.is_valid():
            i = input(
                """Could not find a valid config.
Would you like to create it now? [Y/n]
""")
            if str.lower(i) in ["y", "yes", ""]:
                Configurator(ctx.obj).start()
            else:
                exit(0)
        func(*args, **kwargs)

    return wrapper


@cli.command()
@click.option('-s/-u', '--starred/--unstarred', default=None,
              help="Show only starred/unstarred entries.")
@click.option('-r/-n', '--read/--unread', default=None,
              help="Show only read/unread entries.")
@click.option('-a', '--all', default=False, is_flag=True,
              help="Show read as well as unread entries.")
@click.option('-o', '--oldest', default=False, is_flag=True,
              help="Show oldest matches instead of the newest.")
@click.option('-t', '--trim-output', default=False, is_flag=True,
              help="Trim the titles to fit the length of the cli.")
@click.option('-c', '--count', default=False, is_flag=True,
              help="Show a sum of matching entries.")
@click.option('-q', '--quantity', type=click.INT,
              help="Set the number of entries to show.")
@need_config
@click.pass_context
def list(ctx, starred, read, all, oldest, trim_output, count, quantity):
    """
    List the entries on the wallabag account.

    Gives a summary of entries in wallabag. Use options to filter the results.
    """
    config = ctx.obj
    if all:
        read = None
        starred = None

    if count:
        wallabag_list.count_entries(config, read, starred)
    else:
        wallabag_list.list_entries(
            config, quantity, read, starred, oldest, trim_output)


@cli.command()
@click.option('-c/-n', '--color/--no-color', default=True)
@click.option('-r', '--raw', default=False, is_flag=True,
              help="Disable wordwise trimming.")
@click.option('-t', '--html', default=False, is_flag=True,
              help="Show the entry as html instead of optimized output for \
the cli.")
@click.argument('entry_id', required=True)
@need_config
@click.pass_context
def show(ctx, entry_id, color, raw, html):
    """
    Show the text of an entry.

    The ENTRY_ID can be found with `list` command.
    """
    wallabag_show.show(ctx.obj, entry_id, color, raw, html)


@cli.command()
@click.option('-q', '--quiet', default=False, is_flag=True,
              help="Hide the output if no error occurs.")
@click.argument('entry_id', required=True)
@need_config
def read(entry_id, quiet):
    """
    Toggle the read-status of an existing entry.

    This is an alias for `update --toggle-read <ENTRY_ID>` command.

    The ENTRY_ID can be found with `list` command.
    """
    wallabag_update.update(entry_id, toggle_read=True, quiet=quiet)


@cli.command()
@click.option('-q', '--quiet', default=False, is_flag=True,
              help="Hide the output if no error occurs.")
@click.argument('entry_id', required=True)
@need_config
def star(entry_id, quiet):
    """
    Toggle the starred-status of an existing entry.

    This is an alias for `update --toggle-starred <ENTRY_ID>` command.

    The ENTRY_ID can be found with `list` command.
    """
    wallabag_update.update(entry_id, toggle_star=True, quiet=quiet)


@cli.command()
@click.option('-t', '--title', default="", help="Add a custom title.")
@click.option('-r', '--read', default=False, is_flag=True,
              help="Mark as read.")
@click.option('-s', '--starred', default=False, is_flag=True,
              help="Mark as starred.")
@click.option('-q', '--quiet', default=False, is_flag=True,
              help="Hide the output if no error occurs.")
@click.argument('url', required=True)
@need_config
def add(url, title, read, starred, quiet):
    """Add a new entry to wallabag."""
    wallabag_add.add(url, title, starred, read, quiet)


@cli.command()
@click.option('-f', '--force', default=False, is_flag=True,
              help="Do not ask before deletion.")
@click.option('-q', '--quiet', default=False, is_flag=True,
              help="Hide the output if no error occurs.")
@click.argument('entry_id', required=True)
@need_config
def delete(entry_id, force, quiet):
    """
    Delete an entry from wallabag.

    The ENTRY_ID can be found with `list` command.
    """
    wallabag_delete.delete(entry_id, force, quiet)


@cli.command()
@click.option('-t', '--title', default="", help="Change the title.")
@click.option('-r', '--toggle-read', is_flag=True,
              help="Toggle the read status")
@click.option('-s', '--toggle-starred', is_flag=True,
              help="Toggle the starred status")
@click.option('-q', '--quiet', is_flag=True,
              help="Hide the output if no error occurs.")
@click.argument('entry_id', required=True)
@need_config
@click.pass_context
def update(ctx, entry_id, title, toggle_read, toggle_starred, quiet):
    """
        Toggle the read or starred status or change the title
        of an existing entry.

        The ENTRY_ID can be found with `list` command.
    """
    if not title and not toggle_read and not toggle_starred:
        click.echo("Error: No parameter given.")
        exit(-1)
    wallabag_update.update(
            ctx.obj, entry_id, toggle_read, toggle_starred, title, quiet)


@cli.command()
@click.option('-c', '--check', is_flag=True,
              help="Check the config for errors.")
@click.option('-p', '--password', is_flag=True,
              help="Change the wallabag password.")
@click.option('-o', '--oauth', is_flag=True,
              help="Change the wallabag client credentials.")
@click.pass_context
def config(ctx, check, password, oauth):
    config = ctx.obj
    if check:
        (result, msg) = Validator(config).check()
        click.echo(msg)
        exit(result)
    options = []
    if password or oauth:
        if not config.is_valid():
            click.echo(
                "Invalid existing config.\
                        Therefore you have to enter all values.")
        else:
            if password:
                options.append(PasswordOption())
            if oauth:
                options.append(ClientOption())
                options.append(SecretOption())
    configurator = Configurator(config)
    while True:
        configurator.start(options)
        (result, msg, options) = Validator(config).check_oauth()
        if result or not options:
            click.echo(msg)
            exit(0)
