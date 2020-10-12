# -*- coding: utf-8 -*-
"""Predefined reusable options for the CLI."""
import click

from aiida.cmdline.params.options import OverridableOption

__all__ = ('MAX_ATOMS', 'SKIP_SAFETY', 'CONCURRENT', 'INTERVAL')

MAX_ATOMS = OverridableOption(
    '-M', '--max-atoms', type=click.INT, required=False, help='Filter structures with at most this number of atoms.'
)

NUMBER_SPECIES = OverridableOption(
    '-x',
    '--number-species',
    type=click.INT,
    required=False,
    help='Filter structures with at most this number of species.'
)

SKIP_SAFETY = OverridableOption('--skip-safety', is_flag=True, help='Do not check for excepted and killed processes.')

CONCURRENT = OverridableOption(
    '--concurrent',
    type=click.INT,
    default=300,
    show_default=True,
    help='Number of maximum concurrent work chains to submit.'
)

INTERVAL = OverridableOption(
    '--interval',
    type=click.INT,
    default=600,
    show_default=True,
    help='Number of seconds to sleep after a submit round.'
)
