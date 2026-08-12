# Sentinel SOC Architecture

## Security boundary

``` text
Browser / Collector
        |
        v
   Flask Middleware
        |
        v
    MongoDB Atlas
```

Only the backend communicates with MongoDB.

## Current event pipeline

``` text
Collector
  |
  v
POST /api/ingest
  |
  v
normalize_event()
  |
  v
SecurityEvent validation
  |
  v
analyze_event()
  |
  v
MongoDB
  |
  +--> correlate_event()
  |
  +--> publish()
           |
           v
   /api/events/stream
           |
           v
       Frontend
```

## Planned multi-company model

One database is used for the test environment:

``` text
sentinel
├── companies
├── systems
├── events
└── incidents
```

Every security record is associated with a company and device:

``` text
company_id
system_id
```

IP addresses are recorded as telemetry metadata and are not used as the
permanent device identity.

## Device registration

``` text
First launch
    |
    v
Company name
    |
    v
Company ID
    |
    v
System ID
    |
    v
Hostname/IP collection
    |
    v
POST /api/systems/register
    |
    v
Save local device identity
```

## Isolation rule

The API must determine the permitted company from authenticated client
identity. It must not trust an arbitrary `company_id` supplied by the
browser.

Conceptually:

``` text
Authenticated Company A
        |
        v
API query
        |
        v
WHERE company_id = A
```

Therefore Company A cannot request Company B's events.

## Risk analysis

The analysis engine currently uses deterministic rules. It does not
invent telemetry.

The intended progression is:

``` text
Windows telemetry
 -> normalization
 -> validation
 -> detection
 -> risk score
 -> correlation
 -> incident
```

Real endpoint telemetry will replace synthetic test events as the
collector is developed.
