# -*- coding: utf-8 -*-
"""CLI command to analyse the completion status of the relax stage."""
import click
import tabulate

from . import cmd_completion
from ...params import options

EXTRA_NEW_MAGNETIC_KINDS = 'new_magnetic_kinds'
EXTRA_INVALID_OCCUPATIONS = 'invalid_occupations'


@cmd_completion.command('relax')
@options.MAX_ATOMS()
@options.NUMBER_SPECIES()
def cmd_completion_relax(max_atoms, number_species):
    """Determine the completion rate of the relax step."""
    from aiida import orm

    filters_structure = {'and': []}

    if max_atoms is not None:
        filters_structure['and'].append({'attributes.sites': {'shorter': max_atoms + 1}})

    if number_species is not None:
        filters_structure['and'].append({'attributes.kinds': {'of_length': number_species}})

    query = orm.QueryBuilder()
    query.append(orm.Group, filters={'label': 'structure/unique'}, tag='group')
    query.append(orm.Node, with_group='group', filters=filters_structure)

    nstructures = query.count()

    query = orm.QueryBuilder()
    query.append(orm.Group, filters={'label': 'workchain/relax'}, tag='group')
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

    filters_structure['and'].append({'id': {'!in': submitted}})
    filters_scf = {
        # 'attributes.exit_status': 0,
        # 'extras': {
        #     'and': [{
        #         '!has_key': EXTRA_NEW_MAGNETIC_KINDS
        #     }, {
        #         '!has_key': EXTRA_INVALID_OCCUPATIONS
        #     }]
        # }
    }

    query = orm.QueryBuilder()
    query.append(orm.Group, filters={'label': 'workchain/scf'}, tag='group_scf')
    query.append(orm.WorkChainNode, with_group='group_scf', filters=filters_scf, tag='scf')
    query.append(orm.StructureData, with_outgoing='scf', filters=filters_structure, project='id')
    submittable = set(query.all(flat=True))

    assert set(submittable).intersection(submitted) == set()

    table = [
        ['Structures', nstructures],
        ['Submitted', len(submitted)],
        ['Submitted success', len(success)],
        ['Submitted failed', len(failed)],
        ['Submitted active', len(active)],
        ['Submittable', len(submittable)],
        ['Unsubmittable', nstructures - len(submitted)],
    ]

    click.echo(tabulate.tabulate(table, tablefmt='plain'))
