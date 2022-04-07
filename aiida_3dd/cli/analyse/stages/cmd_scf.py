# -*- coding: utf-8 -*-
"""CLI command to analyse the results of the scf stage."""
import click
import tabulate

from . import cmd_stages
from ...params import options


@cmd_stages.command('scf')
@options.MAX_ATOMS()
def cmd_stage_scf(max_atoms):
    """Commands to analyse the scf stage of the project."""
    import collections

    from aiida.orm import CalcJobNode, Data, Group, QueryBuilder, WorkChainNode, load_group

    group = load_group('workchain/scf')

    filters_structure = {}
    filters_workchain = {'attributes.exit_status': 0}

    if max_atoms is not None:
        filters_structure['attributes.sites'] = {'shorter': max_atoms + 1}

    query = QueryBuilder()
    query.append(Group, filters={'id': group.pk}, tag='group')
    query.append(WorkChainNode, with_group='group', filters=filters_workchain, tag='scf', project='id')
    query.append(CalcJobNode, with_incoming='scf', project='attributes.exit_status')
    query.append(Data, with_outgoing='scf', edge_filters={'label': 'pw__structure'}, filters=filters_structure)

    mapping = collections.defaultdict(list)

    for scf, exit_status in query.iterall():
        mapping[scf].append(exit_status)

    counts = []

    for exit_statuses in mapping.values():
        counts.append(tuple(exit_statuses))

    table = []
    counter = collections.Counter(counts)
    total = sum(counter.values())
    cumulative = 0

    for exit_statuses, count in sorted(counter.items(), key=lambda item: item[1], reverse=True):
        percentage = (count / total) * 100
        cumulative += percentage
        table.append((count, percentage, cumulative, exit_statuses))

    click.echo(tabulate.tabulate(table, headers=['Count', 'Percentage', 'Cumulative', 'Exit statuses']))
