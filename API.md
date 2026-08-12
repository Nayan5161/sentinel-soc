# Sentinel SOC API

## Local base URL

``` text
http://127.0.0.1:8000
```

## Health

``` http
GET /api/health
```

PowerShell:

``` powershell
curl.exe http://127.0.0.1:8000/api/health
```

## Dashboard

``` http
GET /api/dashboard
```

Returns dashboard analytics and recent activity.

## Events

``` http
GET /api/events
```

Parameters:

``` text
limit
suspicious
```

Examples:

``` text
/api/events?limit=50
/api/events?suspicious=true
/api/events?suspicious=false&limit=20
```

## Ingestion

``` http
POST /api/ingest
Content-Type: application/json
```

This is the main middleware ingestion path. Incoming data is normalized,
validated, analyzed, stored and published to the live stream.

## SSE

``` http
GET /api/events/stream
Accept: text/event-stream
```

The React frontend uses this endpoint for live updates.

## Systems

``` http
GET /api/systems
```

## Incidents

``` http
GET /api/incidents
```

## Storage

``` http
GET /api/storage
```

## Planned company/device APIs

``` text
POST /api/companies/register
GET  /api/companies/me

POST /api/systems/register
GET  /api/systems/<system_id>
```

These should be exposed only after authentication and authorization are
implemented.

## Planned reset API

A protected endpoint will provide company-scoped reset:

``` text
POST /api/admin/reset-data
```

The final name and authorization mechanism should be confirmed before
client release.
