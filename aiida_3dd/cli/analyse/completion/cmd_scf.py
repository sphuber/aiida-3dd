# -*- coding: utf-8 -*-
"""CLI command to analyse the completion status of the scf stage."""
import click
import tabulate

from ...params import options
from . import cmd_completion


@cmd_completion.command('scf')
@options.MAX_ATOMS()
@options.NUMBER_SPECIES()
def cmd_completion_scf(max_atoms, number_species):
    """Determine the completion rate of the reconnaissance SCF step."""
    from aiida import orm

    filters_structure = {}

    if max_atoms is not None:
        filters_structure['attributes.sites'] = {'shorter': max_atoms + 1}

    if number_species is not None:
        filters_structure['attributes.kinds'] = {'of_length': number_species}

    query = orm.QueryBuilder()
    query.append(orm.Group, filters={'label': 'structure/unique'}, tag='group')
    query.append(orm.Node, with_group='group', filters=filters_structure)

    nstructures = query.count()

    query = orm.QueryBuilder()
    query.append(orm.Group, filters={'label': 'workchain/scf'}, tag='group')
    query.append(orm.WorkChainNode, with_group='group', tag='workchain', project='attributes.exit_status')
    query.append(orm.StructureData, with_outgoing='workchain', filters=filters_structure, project='id')

    active = []
    failed = []
    success = []
    submitted = []

    for exit_status, pk in query.iterall():
        if exit_status == 0:
            success.append(pk)
        elif exit_status is None:
            active.append(pk)
        else:
            failed.append(pk)

        submitted.append(pk)

    submitted = set(submitted)

    table = [
        ['Structures', nstructures],
        ['Submitted', len(submitted)],
        ['Submitted success', len(success)],
        ['Submitted failed', len(failed)],
        ['Submitted active', len(active)],
        ['Submittable', nstructures - len(submitted)],
    ]

    click.echo(tabulate.tabulate(table, tablefmt='plain'))
