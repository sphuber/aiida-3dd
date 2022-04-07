# -*- coding: utf-8 -*-
# pylint: disable=cyclic-import,wrong-import-position
"""CLI commands to analyse the results of the various project stages."""
from .. import cmd_analyse


@cmd_analyse.group('stages')
def cmd_stages():
    """Commands to analyse the various stages of the project."""


from .cmd_relax import cmd_stage_relax
from .cmd_scf import cmd_stage_scf
