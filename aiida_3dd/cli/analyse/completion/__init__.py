# -*- coding: utf-8 -*-
# pylint: disable=cyclic-import,wrong-import-position
"""CLI commands to analyse the completion status of the various project stages."""
from .. import cmd_analyse


@cmd_analyse.group('completion')
def cmd_completion():
    """Commands to analyse the completion of the various stages of the project."""


from .cmd_relax import cmd_completion_relax
from .cmd_scf import cmd_completion_scf
