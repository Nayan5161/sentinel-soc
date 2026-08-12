# Sentinel SOC Troubleshooting

## Python command not found

Error:

``` text
python : The term 'python' is not recognized
```

Check:

``` powershell
py --version
```

Create the environment:

``` powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Then:

``` powershell
python --version
```

## Wrong virtualenv path

Do not use a Linux/Codespaces path such as:

``` text
/c:/Users/.../.venv/Scripts/python.exe
```

Use Windows syntax:

``` powershell
.\.venv\Scripts\python.exe
```

or activate the environment first.

## MongoDB URI missing

Error:

``` text
RuntimeError: MONGODB_URI is not configured
```

Check:

``` text
backend/.env
```

and make sure the variable name matches `backend/app/config.py`.

Never commit the URI.

## `requests` missing

Error:

``` text
ModuleNotFoundError: No module named 'requests'
```

Install:

``` powershell
python -m pip install requests
```

Then add `requests` to `backend/requirements.txt` so future
installations include it.

## Collector connection refused

Error:

``` text
WinError 10061
```

Cause: the collector tried to contact port 8000 while the backend was
stopped.

Verify:

``` powershell
curl.exe http://127.0.0.1:8000/api/health
```

Start the backend before starting the collector.

## `dev.py` cannot find npm on Windows

Error:

``` text
FileNotFoundError: [WinError 2]
```

The launcher may need `npm.cmd` instead of `npm`.

Workaround:

``` powershell
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

The Windows launcher should be corrected on the new branch.

## Python entered directly into PowerShell

This is Python:

``` python
from app.db import events
```

PowerShell cannot execute it.

Start Python:

``` powershell
python
```

or execute a script:

``` powershell
python reset_data.py
```

For one-line Python:

``` powershell
python -c "from app.db import events; print(events.count_documents({}))"
```

## Ports already in use

``` powershell
netstat -ano | findstr :8000
netstat -ano | findstr :5173
```

Identify a process:

``` powershell
tasklist /FI "PID eq <PID>"
```

Stop it only if it is an old Sentinel process:

``` powershell
taskkill /PID <PID> /F
```

## Live stream disconnected

Test:

``` powershell
curl.exe -N --max-time 10 http://127.0.0.1:8000/api/events/stream
```

Then send an event through `/api/ingest`.

Check:

1.  Flask is running.
2.  Collector can reach port 8000.
3.  `publish()` executes after ingestion.
4.  Frontend uses the correct SSE URL.
5.  Browser connection remains open.

## MongoDB connected but events are empty

Check:

``` powershell
curl.exe http://127.0.0.1:8000/api/health
```

Then:

``` powershell
curl.exe "http://127.0.0.1:8000/api/events?limit=10"
```

If MongoDB is connected but the result is empty, verify that the
collector is successfully calling `/api/ingest`.

## Data reset

The temporary development reset deletes:

``` text
events
systems
incidents
```

and preserves collections/indexes.

Verify after reset:

``` powershell
python -c "from app.db import events,systems,incidents; print('events:',events.count_documents({})); print('systems:',systems.count_documents({})); print('incidents:',incidents.count_documents({}))"
```

Expected:

``` text
events: 0
systems: 0
incidents: 0
```

The final client reset must be company-scoped.

## Security

Never paste the MongoDB URI into GitHub, screenshots, frontend source,
or public documentation. If credentials are exposed, rotate them
immediately.
