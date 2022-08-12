# -*- coding: utf-8 -*-
# pylint: disable=cyclic-import,unused-import,wrong-import-position
"""Module with CLI commands for various analyses."""

from aiida.cmdline.params import arguments
from aiida.cmdline.utils import echo

from .. import cmd_root


@cmd_root.group('analyse')
def cmd_analyse():
    """Commands to analyse the contents of the database."""


@cmd_analyse.command('validation')
@arguments.GROUP()
def cmd_validation(group):
    """Validate the consistency of the various workchain groups."""
    from aiida import orm

    query = orm.QueryBuilder()
    query.append(orm.Group, filters={'label': group.label}, tag='group')
    query.append(orm.Node, with_group='group', tag='wc')
    query.append(orm.StructureData, with_outgoing='wc', project='uuid')

    uuids = query.all(flat=True)

    if len(set(uuids)) != len(uuids):
        echo.echo_critical('there are duplicate structures!')
    else:
        echo.echo_success(f'all good on the western front: found {len(uuids)} structures')


from .completion import cmd_completion
from .results import cmd_results
from .stages import cmd_stages
