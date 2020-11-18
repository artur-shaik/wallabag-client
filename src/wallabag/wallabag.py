#!/usr/bin/env python3

import functools
import logging
import platform
import subprocess
import sys

from colorama import Fore

import click

from wallabag.commands.add import AddCommand, AddCommandParams
from wallabag.commands.anno import (
        AnnoCommand, AnnoSubcommand, AnnoCommandParams)
from wallabag.commands.delete import DeleteCommand, DeleteCommandParams
from wallabag.commands.list import ListCommand, ListParams, CountCommand
from wallabag.commands.show import ShowCommand, ShowCommandParams
from wallabag.commands.tags import (
        TagsCommand, TagsCommandParams, TagsSubcommand)
from wallabag.commands.open import OpenCommand, OpenCommandParams
from wallabag.commands.info import InfoCommand, InfoCommandParams
from wallabag.commands.update import UpdateCommand, UpdateCommandParams
from wallabag.config import Configs
from wallabag.configurator import (
        ClientOption,
        Configurator,
        PasswordOption,
        SecretOption,
        Validator,
    )
from wallabag.commands.update_by_tags import UpdateByTagsCommand
from wallabag.commands.delete_by_tags import DeleteByTags, DeleteByTagsParams
from wallabag import wclick

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def __init_logging(debug, debug_level):
    log_level = logging.getLevelName(debug_level.upper())
    logging.basicConfig(
            level=logging.CRITICAL,
            format=(f'{Fore.YELLOW}%(msecs)d:%(name)s:%(levelname)s: '
                    f'%(message)s{Fore.RESET}'))

    logger = logging.getLogger('wallabag')
    if debug:
        logger.setLevel(log_level)
    else:
        logger.setLevel(logging.CRITICAL)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--config', help='Use custom configuration file')
@click.option('--debug', is_flag=True, help='Enable debug logging to stdout')
@click.option('--debug-level', default='debug', help='Debug level')
@click.version_option(prog_name="wallabag")
@click.pass_context
def cli(ctx, config, debug, debug_level):
    __init_logging(debug, debug_level)

    # Workaround for default non-unicode encodings in the
    # Windows cmd and Powershell
    # -> Analyze encoding and set to utf-8
    if platform.system() == "Windows":
        codepage = subprocess.check_output(['chcp'], shell=True).decode()
        if "65001" not in codepage:
            subprocess.check_output(['chcp', '65001'], shell=True)

    ctx.obj = Configs(config)

    logger = logging.getLogger('wallabag')
    logger.info('wallabag started')


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
                sys.exit(0)
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
@click.option('--trim-output/--no-trim-output', default=True, is_flag=True,
              help="Trim the titles to fit the length of the cli.")
@click.option('-c', '--count', default=False, is_flag=True,
              help="Show a sum of matching entries.")
@click.option('-g', '--tags', help="Return entries that matches ALL tags.")
@click.option('-q', '--quantity', type=click.INT,
              help="Set the number of entries to show.")
@need_config
@click.pass_context
def list(ctx, starred, read, all, oldest, trim_output, count, tags, quantity):
    """
    List the entries on the wallabag account.

    Gives a summary of entries in wallabag. Use options to filter the results.
    """
    config = ctx.obj
    if all:
        read = None
        starred = None

    params = ListParams(quantity, read, starred, oldest, trim_output, tags)
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
@click.option('-a', '--tags', help="Comma-separated list of tags")
@click.option('-q', '--quiet', default=False, is_flag=True,
              help="Hide the output if no error occurs.")
@click.argument('url', required=True)
@need_config
@click.pass_context
def add(ctx, url, title, read, starred, tags, quiet):
    """Add a new entry to wallabag."""
    params = AddCommandParams(url, title, read, starred, tags)
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
@click.option('-f', '--force', default=False, is_flag=True,
              help="Do not ask before deletion.")
@click.option('-q', '--quiet', default=False, is_flag=True,
              help="Hide the output if no error occurs.")
@click.argument('tags', required=True)
@need_config
@click.pass_context
def delete_by_tags(ctx, tags, force, quiet):
    """
    Delete entries from wallabag by tags.

    The TAGS can be found with `tags -c list` command.
    """
    params = DeleteByTagsParams(tags, force, quiet)
    run_command(DeleteByTags(ctx.obj, params), quiet=quiet)


@cli.command()
@click.option('-t', '--title', default="", help="Change the title.")
@click.option('-r', '--toggle-read', is_flag=True,
              help="Toggle the read status")
@click.option('-s', '--toggle-starred', is_flag=True,
              help="Toggle the starred status")
@click.option('--read/--unread', default=None, help="Set the read status")
@click.option('--starred/--unstarred', default=None,
              help="Set the starred status")
@click.option('-q', '--quiet', is_flag=True,
              help="Hide the output if no error occurs.")
@click.argument('entry_id', required=True)
@need_config
@click.pass_context
def update(ctx, entry_id, title, toggle_read, toggle_starred,
           read, starred, quiet):
    """
        Toggle the read or starred status or change the title
        of an existing entry.

        The ENTRY_ID can be found with `list` command.
    """
    params = UpdateCommandParams()
    params.new_title = title
    params.toggle_read = toggle_read
    params.toggle_star = toggle_starred
    params.set_read_state = read
    params.set_star_state = starred
    params.quiet = quiet
    run_command(
            UpdateCommand(ctx.obj, entry_id, params), quiet=quiet)


@cli.command()
@click.option('-r/-n', '--read/--unread', default=None,
              help="Set the read status")
@click.option('-s/-u', '--starred/--unstarred', default=None,
              help="Set the starred status")
@click.option('-f', '--force', is_flag=True,
              help="Do not ask before update.")
@click.option('-q', '--quiet', is_flag=True,
              help="Hide the output if no error occurs.")
@click.argument('tags', required=True)
@need_config
@click.pass_context
def update_by_tags(ctx, tags, read, starred, force, quiet):
    """
        Set the read or starred status of an existing entries
        selected by tags.

        The TAGS can be found with `tags -c list` command.
    """
    params = UpdateCommandParams(False)
    params.set_read_state = read
    params.set_star_state = starred
    params.force = force
    params.quiet = quiet
    run_command(
            UpdateByTagsCommand(ctx.obj, tags, params), quiet=quiet)


@cli.command(short_help="Retrieve and print all tags.")
@click.option('-c', '--command', default=TagsSubcommand.LIST.name,
              type=click.Choice(TagsSubcommand.list(), case_sensitive=False),
              help="Subcommand")
@click.option('-e', '--entry-id', type=int, help="ENTRY ID")
@click.option('-t', '--tags', help="TAGS for subcommands.")
@click.option('--tag-id', type=int,
              help="TAG_ID - used for removing tag by ID")
@need_config
@click.pass_context
def tags(ctx, command, entry_id, tags, tag_id):
    """
    Tag manipulation command.

    list (default) command: Retrieve and print tags in format:

    \b
    {id}. {slug}
    {id}. {slug}
    {id}. {slug}

    If ENTRY_ID specified, make action related to this entry.
    The ENTRY_ID can be found with `list` command.

    add command: Add tags to entry. ENTRY_ID and TAGS should be specified.

    remove command: Remove tag from entry. (ENTRY_ID and TAGS) or TAG_ID
    should be specified.
    """
    params = TagsCommandParams(entry_id=entry_id, tags=tags, tag_id=tag_id)
    params.configure(TagsSubcommand.get(command))
    run_command(TagsCommand(ctx.obj, params))


@cli.command(short_help="Annotation commands.")
@click.option('-c', '--command', default=AnnoSubcommand.LIST.name,
              type=click.Choice(AnnoSubcommand.list(), case_sensitive=False),
              help="Subcommand")
@click.option('-e', '--entry-id', type=int, help="ENTRY ID")
@click.option('-a', '--anno-id', type=int, help="ANNOTATION ID")
@need_config
@click.pass_context
def anno(ctx, command, entry_id, anno_id):
    """
    Annotations manipulation command.

    list (default) command: Retrieve and print annotations for specified entry:

    \b
    {id}. {quote} ({updated}) [{length}]
    {id}. {quote} ({updated}) [{length}]
    {id}. {quote} ({updated}) [{length}]
    """
    params = AnnoCommandParams()
    params.entry_id = entry_id
    params.anno_id = anno_id
    params.command = AnnoSubcommand.get(command)
    run_command(AnnoCommand(ctx.obj, params))


@cli.command(short_help="Get entry information.")
@click.argument('entry_id', required=True)
@need_config
@click.pass_context
def info(ctx, entry_id):
    """
    Show entry information.
    """
    run_command(InfoCommand(ctx.obj, InfoCommandParams(entry_id)))


@cli.command(short_help="Open entry in browser.")
@click.option('-o', '--open-original', is_flag=True,
              help="Open original article")
@click.option('-b', '--browser', type=str, help="Use particular browser")
@click.argument('entry_id', required=True)
@need_config
@click.pass_context
def open(ctx, entry_id, open_original, browser):
    """
    Open entry in browser.

    The `browser` parameter should be one of this list:
    https://docs.python.org/3/library/webbrowser.html#webbrowser.register

    Example: open 10 -b w3m
    """
    run_command(
            OpenCommand(
                ctx.obj, OpenCommandParams(entry_id, open_original, browser)))


@cli.command(short_help="Start configuration.")
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
        run_command(Validator(config))
        sys.exit(0)
    options = []
    if password or oauth:
        if not config.is_valid():
            wclick.echo(
                "Invalid existing config. "
                "Therefore you have to enter all values.")
        else:
            if password:
                options.append(PasswordOption())
            if oauth:
                options.append(ClientOption())
                options.append(SecretOption())
    configurator = Configurator(config)
    while True:
        with wclick.spinner():
            configurator.start(options)
            (result, msg, options) = Validator(config).check_oauth()

        if result or not options:
            wclick.echo(msg)
            sys.exit(0)


def run_command(command, quiet=False):
    with wclick.spinner():
        result, output = command.execute()

    if not quiet and output:
        click.echo(output)
    if not result:
        sys.exit(1)
