# Sentinel SOC

**Development branch:** `feature/company-device-isolation`

Sentinel SOC is a lightweight SOC prototype consisting of a Flask
middleware API, MongoDB Atlas, React/Vite frontend, and a Windows/test
collector.

## Current architecture

``` text
Collector -> Flask API -> Normalizer -> Detection -> MongoDB
                                      |
                                      +-> Correlation -> Incidents
                                      |
                                      +-> SSE -> React Frontend
```

MongoDB is accessed only by the backend. Frontend and collectors
communicate with the API.

## Git versions

-   `main` --- stable existing implementation
-   `v1.0-working` --- preserved checkpoint before the new multi-company
    architecture
-   `feature/company-device-isolation` --- new development

Check the branch before changing code:

``` powershell
git status
git branch
```

Expected:

``` text
* feature/company-device-isolation
```

## Requirements

Windows:

-   Python 3.12
-   Node.js/npm
-   Git
-   MongoDB Atlas connection

Check:

``` powershell
py --version
node --version
npm --version
git --version
```

## First-time Windows setup

``` powershell
git clone https://github.com/Nayan5161/sentinel-soc.git
cd sentinel-soc
git fetch origin
git switch --track origin/feature/company-device-isolation
```

Create the backend environment:

``` powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install frontend packages:

``` powershell
cd ..rontend
npm install
cd ..
```

## MongoDB configuration

Create:

``` text
backend/.env
```

Example:

``` env
MONGO_URI=mongodb+srv://USERNAME:PASSWORD@YOUR-CLUSTER.mongodb.net/?appName=sentinel
MONGO_DB_NAME=sentinel
APP_HOST=0.0.0.0
APP_PORT=8000
CORS_ORIGINS=http://localhost:5173
```

Use the variable names expected by `backend/app/config.py`.

**Never commit `backend/.env` or expose the MongoDB URI.**

## Run the software

From the repository root:

``` powershell
python dev.py
```

Expected services:

``` text
Frontend : http://localhost:5173
Backend  : http://localhost:8000
Health   : http://localhost:8000/api/health
SSE      : http://localhost:8000/api/events/stream
```

## Manual startup

If `dev.py` fails, use three terminals.

### Terminal 1 --- backend

``` powershell
cd backend
.\.venv\Scripts\Activate.ps1
python run.py
```

### Terminal 2 --- frontend

``` powershell
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

### Terminal 3 --- collector

``` powershell
cd backend
.\.venv\Scripts\Activate.ps1
python scripts  est_collector.py
```

## API verification

Use `curl.exe` in PowerShell to avoid PowerShell's `curl` alias:

``` powershell
curl.exe http://127.0.0.1:8000/api/health
```

``` powershell
curl.exe "http://127.0.0.1:8000/api/events?limit=10"
```

``` powershell
curl.exe "http://127.0.0.1:8000/api/events?suspicious=true&limit=10"
```

``` powershell
curl.exe http://127.0.0.1:8000/api/systems
```

## Current API

  Method   Endpoint                        Purpose
  -------- ------------------------------- -------------------------------------------
  GET      `/api/health`                   Backend/database health
  GET      `/api/dashboard`                Dashboard analytics
  GET      `/api/events`                   Latest events
  GET      `/api/events?suspicious=true`   Suspicious events
  GET      `/api/events/stream`            Live SSE stream
  GET      `/api/incidents`                Incidents
  GET      `/api/systems`                  Systems
  GET      `/api/storage`                  Storage information
  POST     `/api/ingest`                   Normalize/analyze/store an incoming event
  POST     `/api/events`                   Store a validated event

## Planned company/device isolation

The new branch will use one MongoDB database with logical tenant
isolation:

``` text
sentinel
├── companies
├── systems
├── events
└── incidents
```

Relevant records will contain:

``` text
company_id
system_id
```

Example:

``` text
Company A
├── SYS-A123
└── SYS-B456

Company B
└── SYS-C789
```

The IP address is metadata, not the permanent device identity. Each
endpoint gets a persistent `system_id`.

The target workflow is:

``` text
First run
  -> ask Company Name
  -> generate Company ID
  -> generate System ID
  -> register device through API
  -> save local identity
  -> start collector
  -> send telemetry
```

The API will enforce company scope so one client cannot read another
client's data.

## Planned reset feature

The final frontend will provide:

``` text
Settings -> Data Management -> Reset My Data
```

The frontend will call a protected backend endpoint. Reset will be
company-scoped:

``` text
Company A reset
    -> delete A events/incidents
    -> preserve A company/device identity
    -> preserve Company B data
```

A full database reset remains a development/admin operation only.

## Risk analysis

The current analysis is deterministic and rule based:

``` text
Telemetry
 -> normalization
 -> validation
 -> detection rules
 -> risk/severity
 -> correlation
 -> incident
 -> dashboard/SSE
```

The collector supplies telemetry; the backend determines whether the
telemetry matches security rules.

The next development stage is to replace synthetic test events with real
Windows telemetry.

## Storage

The test environment has limited storage. Existing retention logic
should be preserved so old event data can be removed when the configured
storage threshold is reached.

## Git development workflow

``` powershell
git status
git diff
git add .
git commit -m "Describe the change"
git push
```

Do not develop the new architecture on `main`.

## Documentation

-   `docs/ARCHITECTURE.md`
-   `docs/API.md`
-   `docs/DEVELOPMENT.md`
-   `docs/TROUBLESHOOTING.md`

## Stop

Press:

``` text
Ctrl+C
```

If a process remains:

``` powershell
netstat -ano | findstr :8000
netstat -ano | findstr :5173
```
