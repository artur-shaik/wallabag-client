# -*- coding: utf-8 -*-

import click
import click_spinner

SPINNER = click_spinner.spinner()


def spinner():
    return SPINNER


def confirm(msg):
    SPINNER.stop()
    result = click.confirm(msg)
    SPINNER.start()
    return result


def echo(msg, *args, **kwargs):
    click.echo(msg, *args, **kwargs)


def prompt(msg, *args, **kwargs):
    SPINNER.stop()
    result = click.prompt(msg, *args, **kwargs)
    SPINNER.start()
    return result
