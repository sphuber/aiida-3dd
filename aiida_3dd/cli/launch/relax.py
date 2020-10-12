# -*- coding: utf-8 -*-
"""Command to launch the relax workflow."""
import click

from aiida.cmdline.params import types
from aiida.cmdline.params import options as options_core
from aiida.cmdline.utils import echo

from ..params import options
from . import cmd_launch


@cmd_launch.command('relax')
@options_core.CODE(required=True, type=types.CodeParamType(entry_point='quantumespresso.pw'),
    default='pw-6.5.0-sirius-6.5.7-gnu@daint-gpu',
    help='Code for `pw.x`.')
@options.CONCURRENT(default=300)
@options.INTERVAL(default=600)
@options.MAX_ATOMS()
@options.SKIP_SAFETY()
@options_core.DRY_RUN()
@options_core.PROFILE(type=types.ProfileParamType(load_profile=True))
@click.pass_context
def launch_relax(ctx, profile, code, concurrent, interval, max_atoms, skip_safety, dry_run):
    """Command to launch the relax workflow."""
    from datetime import datetime
    from time import sleep

    from aiida import orm
    from aiida_quantumespresso_epfl.cli.bulk.pw.relax import launch as launch_workchain

    now = datetime.utcnow().isoformat

    group_scf = orm.Group.get(label='workchain/scf')
    group_relax = orm.Group.get(label='workchain/relax')
    node = None
    max_entries = None
    number_species = None
    skip_check = False
    clean_workdir = True
    pseudo_family = 'SSSP_v1.1_efficiency_PBE'
    force_magnetization = False
    daemon = True
    sirius = True
    num_machines = 6
    max_wallclock_seconds = 24 * 3600
    max_memory_kb = 57042534
    num_mpiprocs_per_machine = 1
    num_cores_per_mpiproc = 12
    verbose = True

    while(True):

        if not skip_safety:
            filters = {'attributes.process_state': {'or': [{'==': 'excepted'}, {'==': 'killed'}]}}
            builder = orm.QueryBuilder().append(orm.ProcessNode, filters=filters)

            if builder.count() > 0:
                echo.echo_critical('found {} excepted or killed processes, exiting'.format(builder.count()))

        filters = {'attributes.process_state': {'or': [{'==': 'waiting'}, {'==': 'running'}, {'==': 'created'}]}}

        builder = orm.QueryBuilder()
        builder.append(orm.Group, filters={'label': group_relax.label}, tag='group')
        builder.append(orm.WorkChainNode, filters=filters, with_group='group')

        current = builder.count()
        max_entries = concurrent - current

        if current < concurrent:
            echo.echo('{} | currently {} running workchains, submitting {} more'.format(now(), current, max_entries))

            inputs = {
                'profile': profile,
                'code': code,
                'group_scf': group_scf,
                'group_relax': group_relax,
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
                'verbose': verbose,
            }
            ctx.invoke(launch_workchain, **inputs)
        else:
            echo.echo('{} | currently {} running workchains, nothing to submit'.format(now(), current))

        echo.echo('{} | sleeping {} seconds'.format(now(), interval))
        sleep(interval)
