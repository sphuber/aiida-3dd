import click
import tabulate

from . import cmd_stages


@cmd_stages.command('relax')
@click.option('-d', '--details', is_flag=True)
def cmd_stage_relax(details):
    """Commands to analyse the relax stage of the project."""
    import collections

    from aiida.orm import load_group, QueryBuilder, Group, WorkChainNode

    group = load_group('workchain/relax')

    if not details:
        query = QueryBuilder()
        query.append(Group, filters={'id': group.pk}, tag='group')
        query.append(WorkChainNode, with_group='group', filters={'attributes.exit_status': 0}, tag='relax', project='id')
        query.append(WorkChainNode, with_incoming='relax', project='id')

        mapping = collections.defaultdict(list)

        for relax, called in query.iterall():
            mapping[relax].append(called)

        counts = []

        for called in mapping.values():
            counts.append(len(called))

        table = []
        counter = collections.Counter(counts)
        total = sum(counter.values())
        cumulative = 0

        for iterations, count in sorted(counter.items(), key=lambda item: item[1], reverse=True):
            percentage = (count / total) * 100
            cumulative += percentage
            table.append((count, percentage, cumulative, iterations))

        click.echo(tabulate.tabulate(table, headers=['Count', 'Percentage', 'Cumulative', 'Iterations']))

    else:
        print('test')