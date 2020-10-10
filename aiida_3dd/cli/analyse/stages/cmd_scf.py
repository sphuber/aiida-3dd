import click
import tabulate

from . import cmd_stages


@cmd_stages.command('scf')
def cmd_stage_scf():
    """Commands to analyse the scf stage of the project."""
    import collections

    from aiida.orm import load_group, QueryBuilder, Group, CalcJobNode, WorkChainNode

    group = load_group('workchain/scf')

    query = QueryBuilder()
    query.append(Group, filters={'id': group.pk}, tag='group')
    query.append(WorkChainNode, with_group='group', filters={'attributes.exit_status': 0}, tag='scf', project='id')
    query.append(CalcJobNode, with_incoming='scf', project='attributes.exit_status')

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
