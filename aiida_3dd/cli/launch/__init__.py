# -*- coding: utf-8 -*-
# pylint: disable=cyclic-import,unused-import,wrong-import-position
"""Module with CLI commands to launch the various workflow steps of the project."""
from .. import cmd_root


@cmd_root.group('launch')
def cmd_launch():
    r"""Commands to launch the various workflow steps of the project.

    The workflow consistes of the following steps, in this order:

    \b
     1. scf
     2. relax
     3. bands
    """


from .relax import launch_relax
# Import the sub commands to register them with the CLI
from .scf import launch_scf
