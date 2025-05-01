# -*- coding: utf-8 -*-

import click
from yaspin import yaspin


SPINNER = None


def spinner():
    global SPINNER
    if not SPINNER:
        SPINNER = yaspin(color="yellow")
    return SPINNER


def stop_spinner():
    spinner().stop()
    pass


def confirm(msg):
    spinner().stop()
    result = click.confirm(msg)
    spinner().start()
    return result


def echo(msg, *args, **kwargs):
    click.echo(msg, *args, **kwargs)


def prompt(msg, *args, **kwargs):
    spinner().stop()
    result = click.prompt(msg, *args, **kwargs)
    spinner().start()
    return result
