# Example scheduled development run

This is a deployment example, not a schedule running in production.
The local CLI has been tested. This deployment has not been started.

Start a local Prefect server in one terminal:

```powershell
prefect server start
```

In another terminal, point the project at that server and run the example:

```powershell
$env:PREFECT_API_URL = "http://127.0.0.1:4200/api"
python -m src.scheduled_example
```

The example serves a baseline deployment at 09:00 Europe/Bucharest.
A served deployment runs while this process is active. It reads the saved
development set and uses the per-response disk cache. No Claude key is needed.
Use a worker/deployment managed by your infrastructure for unattended execution.
Do not schedule the hold-out test as a recurring prompt tuning job.

For a paid API deployment, configure credentials in the execution environment,
decide the model and dataset, and inspect its budget before enabling the schedule.

Reference: [Prefect serve](https://docs.prefect.io/v3/how-to-guides/deployments/create-deployments).
