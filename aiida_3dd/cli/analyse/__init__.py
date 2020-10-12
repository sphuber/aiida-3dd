# -*- coding: utf-8 -*-
# pylint: disable=cyclic-import,unused-import,wrong-import-position
"""Module with CLI commands for various analyses."""
import click
import tabulate

from .. import cmd_root

from aiida.cmdline.params import arguments
from aiida.cmdline.utils import echo
from ..params import options

EXTRA_NEW_MAGNETIC_KINDS = 'new_magnetic_kinds'
EXTRA_INVALID_OCCUPATIONS = 'invalid_occupations'


@cmd_root.group('analyse')
def cmd_analyse():
    """Commands to analyse the contents of the database."""


@cmd_analyse.command('completion')
@arguments.GROUP()
@options.MAX_ATOMS()
@options.NUMBER_SPECIES()
def cmd_stats(group, max_atoms, number_species):
    """Determine the completion rate of the various workchain groups."""
    from aiida import orm

    filters_structure = {'and': []}

    if max_atoms is not None:
        filters_structure['and'].append({'attributes.sites': {'shorter': max_atoms + 1}})

    if number_species is not None:
        filters_structure['and'].append({'attributes.kinds': {'of_length': number_species}})

    query = orm.QueryBuilder()
    query.append(orm.Group, filters={'label': group.label}, tag='group')
    query.append(orm.Node, with_group='group', filters=filters_structure)
    echo.echo(query.count())


@cmd_analyse.command('completion-relax')
@options.MAX_ATOMS()
@options.NUMBER_SPECIES()
def cmd_completion_relax(max_atoms, number_species):
    """Determine the completion rate of the relax step."""
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

    filters_structure['id'] = {'!in': submitted}
    filters_scf = {
        'attributes.exit_status': 0,
        'extras': {
            'and': [
                {'!has_key': EXTRA_NEW_MAGNETIC_KINDS},
                {'!has_key': EXTRA_INVALID_OCCUPATIONS}
            ]
        }
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


@cmd_analyse.command('completion-scf')
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
        ['Submittable', nstructures - len(submitted)]
    ]

    click.echo(tabulate.tabulate(table, tablefmt='plain'))


@cmd_analyse.command('unsubmittable')
def cmd_unsubmittable():
    """Determine the completion rate of the various workchain groups."""
    from aiida import orm

    filters = {
        'or': [{'extras.{}'.format(EXTRA_NEW_MAGNETIC_KINDS): True}, {'extras.{}'.format(EXTRA_INVALID_OCCUPATIONS): True}]
    }

    query = orm.QueryBuilder()
    query.append(orm.Group, filters={'label': 'workchain/scf'}, tag='group')
    query.append(orm.WorkChainNode, with_group='group', filters=filters)
    print(query.count())


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
        echo.echo_success('all good on the western front: found {} structures'.format(len(uuids)))


from .stages import cmd_stages
