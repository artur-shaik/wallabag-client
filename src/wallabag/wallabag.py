#!/usr/bin/env python3

import functools
import platform
import subprocess
from sys import exit

import click

from wallabag.commands.add import AddCommand, AddCommandParams
from wallabag.commands.delete import DeleteCommand, DeleteCommandParams
from wallabag.commands.list import ListCommand, ListParams, CountCommand
from wallabag.commands.show import ShowCommand, ShowCommandParams
from wallabag.commands.update import UpdateCommand, UpdateCommandParams
from wallabag.config import Configs
from wallabag.configurator import (
        ClientOption,
        Configurator,
        PasswordOption,
        SecretOption,
        Validator,
    )


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

    params = ListParams(quantity, read, starred, oldest, trim_output)
    run_command(
            CountCommand(config, params) if count else
            ListCommand(config, params))


@cli.command()
@click.option('-c/-n', '--color/--no-color', default=True)
@click.option('-i', '--image-links', default=False, is_flag=True,
              help="Show image links in optimized output")
@click.option('-r', '--raw', default=False, is_flag=True,
              help="Disable wordwise trimming")
@click.option('-t', '--html', default=False, is_flag=True,
              help="Show the entry as html instead of optimized output for \
the cli.")
@click.argument('entry_id', required=True)
@need_config
@click.pass_context
def show(ctx, entry_id, color, html, raw, image_links):
    """
    Show the text of an entry.

    The ENTRY_ID can be found with `list` command.
    """
    run_command(ShowCommand(
        ctx.obj, ShowCommandParams(entry_id, color, html, raw, image_links)))


@cli.command()
@click.option('-q', '--quiet', default=False, is_flag=True,
              help="Hide the output if no error occurs.")
@click.argument('entry_id', required=True)
@need_config
@click.pass_context
def read(ctx, entry_id, quiet):
    """
    Toggle the read-status of an existing entry.

    This is an alias for `update --toggle-read <ENTRY_ID>` command.

    The ENTRY_ID can be found with `list` command.
    """
    params = UpdateCommandParams(entry_id)
    params.toggle_read = True
    params.quiet = quiet
    run_command(UpdateCommand(ctx.obj, params))


@cli.command()
@click.option('-q', '--quiet', default=False, is_flag=True,
              help="Hide the output if no error occurs.")
@click.argument('entry_id', required=True)
@need_config
@click.pass_context
def star(ctx, entry_id, quiet):
    """
    Toggle the starred-status of an existing entry.

    This is an alias for `update --toggle-starred <ENTRY_ID>` command.

    The ENTRY_ID can be found with `list` command.
    """
    params = UpdateCommandParams(entry_id)
    params.toggle_star = True
    params.quiet = quiet
    run_command(UpdateCommand(ctx.obj, params))


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
@click.pass_context
def add(ctx, url, title, read, starred, quiet):
    """Add a new entry to wallabag."""
    params = AddCommandParams(url, title, read, starred)
    run_command(AddCommand(ctx.obj, params), quiet)


@cli.command()
@click.option('-f', '--force', default=False, is_flag=True,
              help="Do not ask before deletion.")
@click.option('-q', '--quiet', default=False, is_flag=True,
              help="Hide the output if no error occurs.")
@click.argument('entry_id', required=True)
@need_config
@click.pass_context
def delete(ctx, entry_id, force, quiet):
    """
    Delete an entry from wallabag.

    The ENTRY_ID can be found with `list` command.
    """
    params = DeleteCommandParams(entry_id, force, quiet)
    run_command(DeleteCommand(ctx.obj, params))


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
    params = UpdateCommandParams(entry_id)
    params.new_title = title
    params.toggle_read = toggle_read
    params.toggle_star = toggle_starred
    params.quiet = quiet
    run_command(UpdateCommand(ctx.obj, params))


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


def run_command(command, quiet=False):
    result, output = command.run()
    if not quiet and output:
        click.echo(output)
    if not result:
        exit(1)
