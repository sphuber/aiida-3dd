# -*- coding: utf-8 -*-
"""Command to launch the reconnaissance SCF workflow."""
from aiida.cmdline.params import options as options_core
from aiida.cmdline.params import types
from aiida.cmdline.utils import echo
import click

from . import cmd_launch
from ..params import options


@cmd_launch.command('scf')
@options_core.CODE(
    type=types.CodeParamType(entry_point='quantumespresso.pw'),
    default='pw-6.5.0-sirius-6.5.7-gnu@daint-gpu',
    show_default=True,
    help='Code for `pw.x`.'
)
@options.CONCURRENT(default=500)
@options.INTERVAL(default=30)
@options.MAX_ATOMS()
@options.SKIP_SAFETY()
@options_core.DRY_RUN()
@options_core.PROFILE(type=types.ProfileParamType(load_profile=True))
@click.pass_context
def launch_scf(ctx, profile, code, concurrent, interval, max_atoms, skip_safety, dry_run):
    """Command to launch the reconnaissance SCF workflow."""
    from datetime import datetime
    from time import sleep

    from aiida import orm
    from aiida_quantumespresso_epfl.cli.bulk.pw.base import launch as launch_workchain  # pylint: disable=import-error

    now = datetime.utcnow().isoformat

    group_structure = orm.Group.get(label='structure/unique')
    group_workchain = orm.Group.get(label='workchain/scf')
    node = None
    max_entries = None
    number_species = None
    skip_check = False
    clean_workdir = True
    pseudo_family = 'SSSP_v1.1_efficiency_PBE'
    force_magnetization = True
    dry_run = False
    daemon = True
    sirius = True
    num_machines = 4
    max_wallclock_seconds = 12 * 3600
    max_memory_kb = 57042534
    num_mpiprocs_per_machine = 1
    num_cores_per_mpiproc = 12

    while True:

        if not skip_safety:
            filters = {'attributes.process_state': {'or': [{'==': 'excepted'}, {'==': 'killed'}]}}
            builder = orm.QueryBuilder().append(orm.ProcessNode, filters=filters)

            if builder.count() > 0:
                echo.echo_critical(f'found {builder.count()} excepted or killed processes, exiting')

        filters = {'attributes.process_state': {'or': [{'==': 'waiting'}, {'==': 'running'}, {'==': 'created'}]}}

        builder = orm.QueryBuilder()
        builder.append(orm.Group, filters={'label': group_workchain.label}, tag='group')
        builder.append(orm.WorkChainNode, filters=filters, with_group='group')

        current = builder.count()
        max_entries = concurrent - current

        if current < concurrent:
            echo.echo(f'{now()} | currently {current} running workchains, submitting {max_entries} more')

            inputs = {
                'profile': profile,
                'code': code,
                'group_structure': group_structure,
                'group_workchain': group_workchain,
                'node': node,
                'max_entries': max_entries,
                'max_atoms': max_atoms,
                'number_species': number_species,
                'skip_check': skip_check,
                'clean_workdir': clean_workdir,
                'pseudo_family': pseudo_family,
                'force_magnetization': force_magnetization,
                'dry_run': dry_run,
                'daemon': daemon,
                'sirius': sirius,
                'num_machines': num_machines,
                'max_wallclock_seconds': max_wallclock_seconds,
                'max_memory_kb': max_memory_kb,
                'num_mpiprocs_per_machine': num_mpiprocs_per_machine,
                'num_cores_per_mpiproc': num_cores_per_mpiproc,
            }
            ctx.invoke(launch_workchain, **inputs)
        else:
            echo.echo(f'{now()} | currently {current} running workchains, nothing to submit')

        echo.echo(f'{now()} | sleeping {interval} seconds')
        sleep(interval)
