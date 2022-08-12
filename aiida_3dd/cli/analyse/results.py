# -*- coding: utf-8 -*-
# pylint: disable=cyclic-import,unused-import,wrong-import-position
"""Module with CLI commands for various analyses."""
import json

from aiida.cmdline.params import arguments
from aiida.cmdline.utils import echo
import click
import tabulate

from . import cmd_analyse


@cmd_analyse.group('results')
def cmd_results():
    """Commands to analyse the results of the work chains."""


@cmd_results.command('volume-change')
@arguments.GROUP()
@click.option('-L', '--limit', type=click.INT, help='Limit the number of results returned.')
@click.option('--output-file', type=click.File('w', encoding='utf-8'), help='Write output as JSON to file.')
def cmd_volume_change(group, limit, output_file):
    """Analyze the change in cell volume of a structure after the ``PwRelaxWorkChain``."""
    from aiida import orm

    query = orm.QueryBuilder()
    query.append(orm.Group, filters={'label': group.label}, tag='group')
    query.append(orm.Node, with_group='group', tag='wc', filters={'attributes.exit_status': 0})
    query.append(orm.StructureData, with_outgoing='wc', project='*')
    query.append(orm.StructureData, with_incoming='wc', project='*')

    if limit:
        query.limit(limit)

    results = []

    for structure_input, structure_output in query.iterall():

        volume_input = structure_input.get_cell_volume()
        volume_output = structure_output.get_cell_volume()
        volume_difference = volume_output - volume_input
        volume_normalized = volume_difference / volume_input

        results.append((
            volume_normalized,
            volume_difference,
            volume_input,
            volume_output,
            structure_input.get_formula(),
            structure_input.uuid,
            structure_output.uuid,
        ))

    results.sort(key=lambda x: x[0])

    if output_file:
        json.dump(results, output_file, indent=4)
        return

    headers = ['DeltaV/V_in', 'DeltaV', 'V_in', 'V_out', 'UUID input', 'UUID output', 'Formula input', 'Formula output']
    echo.echo(tabulate.tabulate(results, headers=headers))
