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
