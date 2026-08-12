# Sentinel SOC Development Runbook

## Branches

``` text
main
  -> stable existing implementation

v1.0-working
  -> preserved checkpoint

feature/company-device-isolation
  -> new development
```

Check:

``` powershell
git status
git branch
```

The development branch should be active before changes.

## Development cycle

1.  Make one logical change.
2.  Start backend.
3.  Start frontend.
4.  Test API.
5.  Test collector.
6.  Test SSE.
7.  Review Git diff.
8.  Commit.
9.  Push the branch.

Commands:

``` powershell
git status
git diff
git add .
git commit -m "Short description"
git push
```

## Windows setup

``` powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Frontend:

``` powershell
cd ..rontend
npm install
```

## Start

``` powershell
cd ..
python dev.py
```

## Manual start

Backend:

``` powershell
cd backend
.\.venv\Scripts\Activate.ps1
python run.py
```

Frontend:

``` powershell
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

Collector:

``` powershell
cd backend
.\.venv\Scripts\Activate.ps1
python scripts  est_collector.py
```

## Data reset

The temporary development reset script can be run from `backend`:

``` powershell
python reset_data.py
```

It was used during development to clear events, systems and incidents.

The future frontend reset must be authenticated and company-scoped. Do
not expose a global database-delete operation to clients.
