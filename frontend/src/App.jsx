import { useEffect, useMemo, useState } from 'react'
import {
  Activity,
  AlertTriangle,
  Bell,
  Bot,
  CheckCircle2,
  CircleAlert,
  Database,
  Globe2,
  HeartPulse,
  Network,
  Server,
  Shield,
  ShieldAlert,
  Terminal,
  Wifi,
  XCircle,
  Zap,
} from 'lucide-react'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import './App.css'

function formatTime(value) {
  if (!value) return '--'

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return '--'
  }

  return date.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function severityClass(severity) {
  return String(severity || 'info').toLowerCase()
}

function severityLabel(severity) {
  return String(severity || 'info').toUpperCase()
}

function MetricCard({ icon: Icon, label, value, detail, danger }) {
  return (
    <div className={`metric-card ${danger ? 'danger' : ''}`}>
      <div className="metric-icon">
        <Icon size={20} />
      </div>

      <div>
        <div className="metric-label">{label}</div>
        <div className="metric-value">{value}</div>
        {detail && <div className="metric-detail">{detail}</div>}
      </div>
    </div>
  )
}

function App() {
  const [dashboard, setDashboard] = useState(null)
  const [events, setEvents] = useState([])
  const [incidents, setIncidents] = useState([])
  const [connected, setConnected] = useState(false)
  const [lastSync, setLastSync] = useState(null)
  const [error, setError] = useState(null)

  async function loadDashboard() {
    try {
      const response = await fetch('/api/dashboard')

      if (!response.ok) {
        throw new Error(`Dashboard API returned ${response.status}`)
      }

      const data = await response.json()

      setDashboard(data)
      setLastSync(new Date())
      setError(null)
    } catch (err) {
      setError(err.message)
    }
  }

  async function loadEvents() {
    try {
      const response = await fetch('/api/events?limit=50')

      if (!response.ok) {
        throw new Error(`Events API returned ${response.status}`)
      }

      const data = await response.json()

      setEvents(data)
    } catch (err) {
      console.error(err)
    }
  }

  async function loadIncidents() {
    try {
      const response = await fetch('/api/incidents')

      if (!response.ok) {
        throw new Error(`Incidents API returned ${response.status}`)
      }

      const data = await response.json()

      setIncidents(data)
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    loadDashboard()
    loadEvents()
    loadIncidents()

    const interval = setInterval(() => {
      loadDashboard()
      loadIncidents()
    }, 10000)

    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const source = new EventSource('/api/events/stream')

    source.onopen = () => {
      setConnected(true)
    }

    source.addEventListener('security_event', (message) => {
      try {
        const payload = JSON.parse(message.data)

        if (payload?.event) {
          setEvents((previous) => [
            payload.event,
            ...previous.filter(
              (event) =>
                event.event_id !== payload.event.event_id
            ),
          ].slice(0, 50))
        }

        setLastSync(new Date())

        loadDashboard()
        loadIncidents()
      } catch (err) {
        console.error('Invalid SSE event:', err)
      }
    })

    source.onerror = () => {
      setConnected(false)
    }

    return () => {
      source.close()
    }
  }, [])

  const severityData = useMemo(() => {
    const severity = dashboard?.severity || {}

    return [
      {
        name: 'Critical',
        value: severity.critical || 0,
      },
      {
        name: 'High',
        value: severity.high || 0,
      },
      {
        name: 'Medium',
        value: severity.medium || 0,
      },
      {
        name: 'Low',
        value: severity.low || 0,
      },
      {
        name: 'Info',
        value: severity.info || 0,
      },
    ]
  }, [dashboard])

  const totalSystems = dashboard?.systems?.total || 0
  const onlineSystems = dashboard?.systems?.online || 0

  const securityScore = dashboard?.security_score ?? 0
  const suspicious = dashboard?.events?.suspicious ?? 0
  const totalEvents = dashboard?.events?.total ?? 0

  return (
    <div className="app-shell">

      <header className="topbar">

        <div className="brand">
          <div className="brand-icon">
            <Shield size={25} />
          </div>

          <div>
            <div className="brand-title">
              SENTINEL <span>AI</span>
            </div>

            <div className="brand-subtitle">
              CYBER DEFENSE COMMAND CENTER
            </div>
          </div>
        </div>

        <div className="top-status">

          <div className="status-chip">
            <span
              className={`status-dot ${
                connected ? 'online' : 'offline'
              }`}
            />

            {connected ? 'LIVE STREAM' : 'DISCONNECTED'}
          </div>

          <div className="status-chip">
            <Activity size={15} />
            {dashboard?.threat_level || 'UNKNOWN'}
          </div>

          <div className="status-chip">
            <Bell size={15} />
            {dashboard?.active_incidents ?? 0} INCIDENTS
          </div>

        </div>

      </header>

      <div className="threat-ticker">
        <span className="ticker-title">
          <span className="ticker-dot" />
          LIVE SECURITY ACTIVITY
        </span>

        <span>
          {events.length > 0
            ? events[0]?.event?.message || 'Waiting for events'
            : 'Waiting for incoming security events'}
        </span>

        <span>
          Last sync: {formatTime(lastSync)}
        </span>
      </div>

      <main className="dashboard">

        {error && (
          <div className="error-banner">
            <CircleAlert size={18} />
            Backend connection error: {error}
          </div>
        )}

        <section className="hero-grid">

          <div className="score-card">

            <div className="section-title">
              <ShieldAlert size={19} />
              MISSION CONTROL
            </div>

            <div className="score-layout">

              <div className="score-ring">
                <div className="score-inner">
                  <div className="score-number">
                    {securityScore}
                    <span>%</span>
                  </div>

                  <div className="score-label">
                    SECURITY SCORE
                  </div>

                  <div className="score-status">
                    {securityScore >= 80
                      ? 'STRONG POSTURE'
                      : securityScore >= 60
                        ? 'MODERATE POSTURE'
                        : 'ACTION REQUIRED'}
                  </div>
                </div>
              </div>

              <div className="hero-metrics">

                <MetricCard
                  icon={Server}
                  label="SYSTEMS ONLINE"
                  value={`${onlineSystems} / ${totalSystems}`}
                />

                <MetricCard
                  icon={ShieldAlert}
                  label="SUSPICIOUS EVENTS"
                  value={suspicious}
                  danger={suspicious > 0}
                />

                <MetricCard
                  icon={Database}
                  label="EVENTS INGESTED"
                  value={totalEvents}
                />

                <MetricCard
                  icon={AlertTriangle}
                  label="ACTIVE INCIDENTS"
                  value={dashboard?.active_incidents ?? 0}
                  danger={
                    (dashboard?.active_incidents ?? 0) > 0
                  }
                />

              </div>

            </div>
          </div>

        </section>

        <section className="stats-grid">

          <MetricCard
            icon={Database}
            label="TOTAL EVENTS"
            value={totalEvents}
            detail="Last 24 hours"
          />

          <MetricCard
            icon={Shield}
            label="SECURITY SCORE"
            value={`${securityScore}%`}
            detail="Calculated from observed events"
          />

          <MetricCard
            icon={AlertTriangle}
            label="HIGH / CRITICAL"
            value={
              (dashboard?.severity?.high || 0) +
              (dashboard?.severity?.critical || 0)
            }
            danger={
              (dashboard?.severity?.high || 0) +
              (dashboard?.severity?.critical || 0) > 0
            }
          />

          <MetricCard
            icon={Network}
            label="SYSTEMS"
            value={totalSystems}
            detail={`${onlineSystems} currently online`}
          />

        </section>

        <section className="content-grid">

          <div className="panel">

            <div className="panel-header">
              <div className="section-title">
                <Activity size={18} />
                THREAT ACTIVITY
              </div>

              <span className="live-badge">
                {connected ? '● STREAMING' : '○ OFFLINE'}
              </span>
            </div>

            <div className="chart">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={severityData}>
                  <defs>
                    <linearGradient
                      id="eventGradient"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop
                        offset="0%"
                        stopColor="#16e0d0"
                        stopOpacity={0.35}
                      />
                      <stop
                        offset="100%"
                        stopColor="#16e0d0"
                        stopOpacity={0}
                      />
                    </linearGradient>
                  </defs>

                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#1d2935"
                  />

                  <XAxis
                    dataKey="name"
                    stroke="#64748b"
                  />

                  <YAxis stroke="#64748b" />

                  <Tooltip
                    contentStyle={{
                      background: '#0b1118',
                      border: '1px solid #263441',
                      color: '#fff',
                    }}
                  />

                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="#16e0d0"
                    fill="url(#eventGradient)"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>

          </div>

          <div className="panel">

            <div className="panel-header">

              <div className="section-title">
                <AlertTriangle size={18} />
                EVENTS BY SEVERITY
              </div>

              <span className="panel-caption">
                Backend analysis
              </span>

            </div>

            <div className="chart">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={severityData}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#1d2935"
                  />

                  <XAxis
                    dataKey="name"
                    stroke="#64748b"
                  />

                  <YAxis stroke="#64748b" />

                  <Tooltip
                    contentStyle={{
                      background: '#0b1118',
                      border: '1px solid #263441',
                      color: '#fff',
                    }}
                  />

                  <Bar
                    dataKey="value"
                    fill="#16e0d0"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>

          </div>

        </section>

        <section className="content-grid">

          <div className="panel">

            <div className="panel-header">

              <div className="section-title">
                <Terminal size={18} />
                LIVE ACTIVITY FEED
              </div>

              <span className="live-badge">
                {connected ? '● LIVE' : '○ WAITING'}
              </span>

            </div>

            <div className="event-list">

              {events.length === 0 ? (
                <div className="empty-state">
                  <Wifi size={25} />
                  <p>
                    No security events received yet.
                  </p>
                  <span>
                    Waiting for telemetry...
                  </span>
                </div>
              ) : (

                events.slice(0, 15).map((event) => {

                  const severity =
                    event.analysis?.severity ||
                    event.event?.severity ||
                    'info'

                  const suspicious =
                    event.analysis?.suspicious ||
                    event.detection?.suspicious

                  return (
                    <div
                      className="event-row"
                      key={
                        event.event_id ||
                        event._id
                      }
                    >

                      <div
                        className={`event-icon ${severityClass(
                          severity
                        )}`}
                      >
                        {suspicious ? (
                          <ShieldAlert size={17} />
                        ) : (
                          <CheckCircle2 size={17} />
                        )}
                      </div>

                      <div className="event-main">

                        <div className="event-top">

                          <span className="event-source">
                            {event.source?.source_type ||
                              'unknown'}
                          </span>

                          <span
                            className={`severity ${severityClass(
                              severity
                            )}`}
                          >
                            {severityLabel(severity)}
                          </span>

                        </div>

                        <div className="event-message">
                          {event.analysis?.explanation ||
                            event.event?.message ||
                            'Security event received'}
                        </div>

                        <div className="event-meta">

                          {event.actor?.user && (
                            <span>
                              USER: {event.actor.user}
                            </span>
                          )}

                          {event.actor?.ip && (
                            <span>
                              IP: {event.actor.ip}
                            </span>
                          )}

                          {event.analysis?.rule_name && (
                            <span>
                              RULE: {event.analysis.rule_name}
                            </span>
                          )}

                        </div>

                      </div>

                      <div className="event-time">
                        {formatTime(
                          event.timestamp ||
                            event.received_at
                        )}
                      </div>

                    </div>
                  )
                })
              )}

            </div>

          </div>

          <div className="panel">

            <div className="panel-header">

              <div className="section-title">
                <Bot size={18} />
                AI / ANALYSIS INSIGHTS
              </div>

              <span className="ai-badge">
                ANALYSIS
              </span>

            </div>

            <div className="insights">

              {events.length === 0 && (
                <div className="insight neutral">
                  <Activity size={17} />
                  Waiting for security telemetry.
                </div>
              )}

              {events
                .filter(
                  (event) =>
                    event.analysis ||
                    event.detection?.suspicious
                )
                .slice(0, 8)
                .map((event) => {

                  const analysis = event.analysis || {}

                  return (
                    <div
                      className={`insight ${
                        severityClass(
                          analysis.severity
                        )
                      }`}
                      key={`analysis-${
                        event.event_id ||
                        event._id
                      }`}
                    >

                      <div className="insight-icon">
                        {analysis.suspicious ? (
                          <ShieldAlert size={17} />
                        ) : (
                          <CheckCircle2 size={17} />
                        )}
                      </div>

                      <div>

                        <div className="insight-title">
                          {analysis.rule_name ||
                            'Routine Activity'}
                        </div>

                        <div className="insight-text">
                          {analysis.explanation ||
                            'No immediate security concern detected.'}
                        </div>

                        {analysis.recommendation && (
                          <div className="insight-recommendation">
                            {analysis.recommendation}
                          </div>
                        )}

                      </div>

                    </div>
                  )
                })}

            </div>

          </div>

        </section>

        <section className="panel">

          <div className="panel-header">

            <div className="section-title">
              <ShieldAlert size={18} />
              ACTIVE INCIDENTS
            </div>

            <span className="panel-caption">
              Correlation engine
            </span>

          </div>

          {incidents.length === 0 ? (
            <div className="empty-state compact">
              <CheckCircle2 size={22} />
              <span>No active correlated incidents.</span>
            </div>
          ) : (

            <div className="incident-list">

              {incidents.map((incident) => (

                <div
                  className="incident-row"
                  key={
                    incident.incident_id ||
                    incident._id
                  }
                >

                  <div
                    className={`incident-severity ${severityClass(
                      incident.severity
                    )}`}
                  >
                    <ShieldAlert size={19} />
                  </div>

                  <div className="incident-main">

                    <div className="incident-title">
                      {incident.title}
                    </div>

                    <div className="incident-description">
                      {incident.explanation}
                    </div>

                    <div className="incident-meta">
                      {incident.source_ip &&
                        `SOURCE ${incident.source_ip}`}
                      {incident.username &&
                        ` · USER ${incident.username}`}
                      {incident.event_count &&
                        ` · ${incident.event_count} EVENTS`}
                    </div>

                  </div>

                  <div className="incident-risk">

                    <div className="risk-score">
                      {incident.risk_score}
                    </div>

                    <div className="risk-label">
                      RISK
                    </div>

                  </div>

                </div>

              ))}

            </div>
          )}

        </section>

        <footer className="footer">

          <span>
            SENTINEL AI SOC
          </span>

          <span>
            MongoDB • Flask • React • SSE
          </span>

          <span>
            <Zap size={13} />
            Real-time telemetry
          </span>

        </footer>

      </main>

    </div>
  )
}

export default App
