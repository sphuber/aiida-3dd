# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position,wildcard-import
"""Module for the command line interface."""
from aiida.cmdline.params import options, types
import click
import click_completion

# Activate the completion of parameter types provided by the click_completion package
click_completion.init()


@click.group('aiida-3dd', context_settings={'help_option_names': ['-h', '--help']})
@options.PROFILE(type=types.ProfileParamType(load_profile=True), expose_value=False)
def cmd_root():
    """CLI for the 3DD project."""


from .analyse import *
from .launch import *
