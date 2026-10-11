"""Bounded real scheduler smoke test: isolated server, one offline flow, then pause."""
import asyncio
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen

from src.config import PROJECT_ROOT
from src.mapqa_data import save_json
from src.mapqa_benchmark import OUTPUT


async def _scheduled_run(api_url):
    from prefect.client.orchestration import get_client
    from prefect.client.schemas.filters import DeploymentFilter, DeploymentFilterId
    from prefect.client.schemas.schedules import IntervalSchedule
    from prefect.client.schemas.sorting import FlowRunSort
    from prefect.runner import Runner
    from prefect.exceptions import ObjectNotFound
    from prefect.settings import temporary_settings, PREFECT_API_URL
    from src.mapqa_flow import mapqa_flow
    with temporary_settings(updates={PREFECT_API_URL:api_url}):
        runner=Runner(name='bounded-mapqa-smoke',query_seconds=1,prefetch_seconds=0,pause_on_shutdown=True,limit=1)
        schedule=IntervalSchedule(interval=timedelta(seconds=60),anchor_date=datetime.now(timezone.utc)+timedelta(seconds=20))
        deployment=await mapqa_flow.to_deployment(name='bounded-offline-schedule',schedule=schedule,
                                           parameters={'mode':'rules','cached_only':True})
        deployment_id=await runner.aadd_deployment(deployment)
        task=asyncio.create_task(runner.start())
        observed=[]
        try:
            async with get_client() as client:
                deadline=time.monotonic()+180
                chosen=None
                paused=False
                while time.monotonic()<deadline:
                    runs=await client.read_flow_runs(deployment_filter=DeploymentFilter(id=DeploymentFilterId(any_=[deployment_id])),
                                                    limit=20,sort=FlowRunSort.EXPECTED_START_TIME_ASC)
                    if runs and chosen is None:
                        chosen=min(runs,key=lambda r:r.expected_start_time).id
                    completed=[r for r in runs if r.state and r.state.is_completed()]
                    if completed:
                        chosen=min(completed,key=lambda r:r.expected_start_time).id
                    # Use a direct read: pagination must not hide a chosen running run.
                    try:
                        run=await client.read_flow_run(chosen) if chosen else None
                    except ObjectNotFound:
                        # A rescheduled/deleted future run is not a failed flow.
                        chosen=None
                        await asyncio.sleep(1)
                        continue
                    if run:
                        state=run.state.name if run.state else 'unknown'
                        if not observed or observed[-1]['state']!=state:
                            observed.append({'state':state,'observed_at':datetime.now(timezone.utc).isoformat()})
                            print('Scheduled smoke: '+state,flush=True)
                        # Pausing a deployment can delete its future Scheduled runs.
                        # Wait until our chosen run is executing before pausing.
                        if not paused and run.state and (run.state.is_running() or run.state.is_final()):
                            await client.set_deployment_paused_state(deployment_id,True)
                            paused=True
                        if run.state and run.state.is_final():
                            report={'deployment_id':str(deployment_id),'flow_run_id':str(run.id),
                                    'state':state,'schedule_interval_seconds':60,'observed_states':observed,
                                    'run_created_by_scheduler':run.auto_scheduled,
                                    'scheduled_start':str(run.expected_start_time),
                                    'deployment_paused':True,'local_only':True,'runner_stopped_after_test':True}
                            if not run.state.is_completed(): raise RuntimeError('Scheduled flow failed: '+state)
                            if not run.auto_scheduled: raise RuntimeError('Run was not created by scheduler')
                            return report
                    await asyncio.sleep(1)
                raise TimeoutError('Scheduler smoke did not finish within 180 seconds')
        finally:
            async with get_client() as client:
                await client.set_deployment_paused_state(deployment_id,True)
            await runner.astop()
            await asyncio.wait_for(task,30)


def smoke_schedule():
    with socket.socket() as probe:
        probe.bind(('127.0.0.1',0))
        port=probe.getsockname()[1]
    with tempfile.TemporaryDirectory(prefix='mapqa-scheduler-') as temporary:
        env=os.environ.copy()
        env.update(PREFECT_SERVER_DATABASE_CONNECTION_URL='sqlite+aiosqlite:///'+str(Path(temporary)/'schedule.db'),
                   PREFECT_SERVER_SERVICES_SCHEDULER_LOOP_SECONDS='2',
                   PREFECT_SERVER_ANALYTICS_ENABLED='false',PREFECT_API_URL=f'http://127.0.0.1:{port}/api',
                   LANGSMITH_TRACING='false',LANGCHAIN_TRACING_V2='false')
        with (Path(temporary)/'server.log').open('w',encoding='utf-8') as log:
            server=subprocess.Popen([sys.executable,'-m','prefect','server','start','--host','127.0.0.1','--port',str(port)],
                                    cwd=PROJECT_ROOT,env=env,stdout=log,stderr=log,
                                    creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            try:
                deadline=time.monotonic()+60
                while time.monotonic()<deadline:
                    try:
                        with urlopen(f'http://127.0.0.1:{port}/api/health',timeout=1): break
                    except OSError:
                        if server.poll() is not None: raise RuntimeError('Isolated Prefect server exited')
                        time.sleep(.5)
                else: raise TimeoutError('Isolated Prefect server failed to start')
                report=asyncio.run(_scheduled_run(f'http://127.0.0.1:{port}/api'))
            finally:
                server.terminate()
                try: server.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    server.kill(); server.wait(timeout=10)
    save_json(OUTPUT/'schedule_smoke.json',report)
    return report
