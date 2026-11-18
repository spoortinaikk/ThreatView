
import React, { useEffect, useMemo, useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LineChart,
  Line,
  Legend
} from "recharts";
import ThreatMap from "./ThreatMap";
import "./styles.css";

const API_BASE = "/api";

async function request(path, options = {}, apiKey = "") {
  const headers = { ...(options.headers || {}) };

  if (apiKey) headers["X-API-Key"] = apiKey;

  if (options.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed (${response.status})`);
  }

  const contentType = response.headers.get("content-type") || "";

  return contentType.includes("application/json")
    ? response.json()
    : response;
}

const PERIODS = [
  { label: "Last 24 hours", value: "1" },
  { label: "Last 48 hours", value: "2" },
  { label: "Last 7 days", value: "7" },
  { label: "Last 30 days", value: "30" }
];

const SORT_FIELDS = {
  Indicator: "value",
  Type: "ioc_type",
  Source: "source",
  Severity: "severity",
  "First seen": "first_seen"
};

const CHART_COLORS = [
  "#09a9ff",
  "#8b6cff",
  "#00d6a0",
  "#ffae22",
  "#ff4e70",
  "#54c7ec"
];

function prettyNumber(value) {
  return Number(value || 0).toLocaleString();
}

function normalizeTrendData(rows) {
  if (!Array.isArray(rows)) return [];

  const grouped = {};

  rows.forEach((row) => {
    const day = row.day || row.date || row.time || "Unknown";
    const family = row.family || "Unknown";
    const count = Number(row.count || 0);

    if (!grouped[day]) {
      grouped[day] = { date: day };
    }

    grouped[day][family] = (grouped[day][family] || 0) + count;
  });

  return Object.values(grouped).sort((a, b) =>
    String(a.date).localeCompare(String(b.date))
  );
}

function normalizeCountries(rows) {
  if (!Array.isArray(rows)) return [];

  const aliases = {
    UK: "GB",
    USA: "US"
  };

  return rows
    .map((item) => {
      const rawName = String(item?.name || "")
        .trim()
        .toUpperCase();

      return {
        ...item,
        name: aliases[rawName] || rawName,
        count: Number(item?.count || 0)
      };
    })
    .filter((item) =>
      item.name &&
      !["UNKNOWN", "UN", "NULL", "N/A", "NONE"].includes(item.name) &&
      /^[A-Z]{2}$/.test(item.name) &&
      item.count > 0
    )
    .reduce((result, item) => {
      const existing = result.find((entry) => entry.name === item.name);

      if (existing) {
        existing.count += item.count;
      } else {
        result.push({ ...item });
      }

      return result;
    }, [])
    .sort((a, b) => b.count - a.count);
}

export default function App() {
  const [apiKey, setApiKey] = useState(
    () => localStorage.getItem("threatview_api_key") || ""
  );

  const [period, setPeriod] = useState("1");
  const [stats, setStats] = useState(null);
  const [mapStats, setMapStats] = useState(null);
  const [trends, setTrends] = useState([]);
  const [iocs, setIocs] = useState([]);
  const [me, setMe] = useState(null);

  const [sort, setSort] = useState("first_seen");
  const [order, setOrder] = useState("desc");

  const [query, setQuery] = useState("");
  const [searchResult, setSearchResult] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [activeNav, setActiveNav] = useState("Overview");

  const [registerEmail, setRegisterEmail] = useState("");
  const [industry, setIndustry] = useState("");
  const [domain, setDomain] = useState("");
  const [registerResult, setRegisterResult] = useState(null);

  const isPro = me?.tier === "pro";

  const availablePeriods = isPro
    ? PERIODS
    : PERIODS.slice(0, 1);

  useEffect(() => {
    if (!isPro && period !== "1") {
      setPeriod("1");
    }
  }, [isPro, period]);

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
      setLoading(true);
      setError("");

      try {
        const [profile, summary, trendData, list, mapData] =
  await Promise.all([
    request("/me", {}, apiKey).catch(() => null),
    request(`/stats?days=${period}`, {}, apiKey),
    request(`/trends?days=${period}`, {}, apiKey),
    request(
      `/iocs?days=${period}&sort=${sort}&order=${order}&limit=50`,
      {},
      apiKey
    ),
    request("/map-stats", {}, apiKey)
  ]);
        

        if (cancelled) return;

        setMe(profile);
        setStats(summary);
        setMapStats(mapData);

        setTrends(
          normalizeTrendData(
            Array.isArray(trendData)
              ? trendData
              : trendData?.trends || []
          )
        );

        setIocs(
          Array.isArray(list)
            ? list
            : list?.items || list?.iocs || []
        );
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Could not load dashboard data.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadDashboard();

    return () => {
      cancelled = true;
    };
  }, [apiKey, period, sort, order]);

  const total = stats?.total ?? stats?.count ?? iocs.length;

  const severityRows = [
    {
      label: "High Severity",
      value: stats?.high ?? 0,
      className: "high",
      icon: "!"
    },
    {
      label: "Medium Severity",
      value: stats?.medium ?? 0,
      className: "medium",
      icon: "!"
    },
    {
      label: "Low Severity",
      value: stats?.low ?? 0,
      className: "low",
      icon: "!"
    },
    {
      label: "Total Indicators",
      value: total,
      className: "total",
      icon: "◆"
    }
  ];

  const countryData = useMemo(
    () => normalizeCountries(stats?.countries || []),
    [stats?.countries]
  );

  const malwareData = useMemo(() => trends, [trends]);

  const malwareFamilies = useMemo(() => {
    const families = new Set();

    malwareData.forEach((row) => {
      Object.keys(row).forEach((key) => {
        if (key !== "date") families.add(key);
      });
    });

    return Array.from(families).slice(0, 6);
  }, [malwareData]);

  const scrollToSection = (sectionId, label) => {
    setActiveNav(label);

    document.getElementById(sectionId)?.scrollIntoView({
      behavior: "smooth",
      block: "start"
    });
  };

  const runSearch = async (event) => {
    event.preventDefault();

    if (!query.trim()) return;

    setSearchResult(null);
    setError("");

    try {
      const result = await request(
        `/search?q=${encodeURIComponent(query.trim())}`,
        {},
        apiKey
      );

      setSearchResult(result);
    } catch (err) {
      setError(err.message);
    }
  };

  const register = async (event) => {
    event.preventDefault();

    setRegisterResult(null);
    setError("");

    try {
      const params = new URLSearchParams({
        email: registerEmail,
        industry,
        domain
      });

      const result = await request(
        `/register?${params.toString()}`,
        { method: "POST" }
      );

      setRegisterResult(result);

      if (result.api_key) {
        setApiKey(result.api_key);
        localStorage.setItem("threatview_api_key", result.api_key);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const saveApiKey = (value) => {
    setApiKey(value);

    if (value) {
      localStorage.setItem("threatview_api_key", value);
    } else {
      localStorage.removeItem("threatview_api_key");
    }
  };

  const changeSort = (field) => {
    if (sort === field) {
      setOrder((current) =>
        current === "desc" ? "asc" : "desc"
      );
    } else {
      setSort(field);
      setOrder("desc");
    }
  };

  const exportCsv = async () => {
    try {
      const response = await fetch(
        `${API_BASE}/export.csv?days=30`,
        {
          headers: apiKey
            ? { "X-API-Key": apiKey }
            : {}
        }
      );

      if (!response.ok) {
        throw new Error(
          (await response.text()) ||
          "CSV export is available to Pro accounts."
        );
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");

      anchor.href = url;
      anchor.download = "threatview-export.csv";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();

      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message);
    }
  };

  const openReport = () => {
    window.open(
      `${API_BASE}/report.pdf`,
      "_blank",
      "noopener,noreferrer"
    );
  };

  return (
    <div className="tv-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <span>T</span>
          </div>

          <div>
            <strong>ThreatView</strong>
            <small>
              THREAT<br />
              INTELLIGENCE
            </small>
          </div>
        </div>

        <div className="side-label">WORKSPACE</div>

        <button
          className={`nav-item ${activeNav === "Overview" ? "active" : ""}`}
          onClick={() => scrollToSection("overview", "Overview")}
        >
          <span className="nav-icon">•</span>
          Overview
        </button>

        <button
          className={`nav-item ${activeNav === "Threat Indicators" ? "active" : ""}`}
          onClick={() => scrollToSection("indicators", "Threat Indicators")}
        >
          <span className="nav-icon">◇</span>
          Threat Indicators
        </button>

        <button
          className={`nav-item ${activeNav === "Threat Analytics" ? "active" : ""}`}
          onClick={() => scrollToSection("analytics", "Threat Analytics")}
        >
          <span className="nav-icon">↗</span>
          Threat Analytics
        </button>

        <button
          className={`nav-item ${activeNav === "Register Account" ? "active" : ""}`}
          onClick={() => scrollToSection("account", "Register Account")}
        >
          <span className="nav-icon">+</span>
          Register Account
        </button>

        <div className="side-label report-label">REPORTS</div>

        <button className="nav-item" onClick={openReport}>
          <span className="nav-icon">▤</span>
          Weekly PDF Report
        </button>

        <button className="export-button" onClick={exportCsv}>
          <span>⇩</span> Export CSV
        </button>

        <div className="sidebar-footer">
          <i /> Dashboard available
          <p>ThreatView Security Platform</p>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb">
            <span>◆</span> Workspace <b>/</b> {activeNav}
          </div>

          <div className="top-actions">
            <span className="plan-pill">
              ♛ {isPro ? "PRO PLAN" : "FREE PLAN"}
            </span>
            <span className="avatar">TV</span>
          </div>
        </header>

        <section className="content" id="overview">
          <div className="page-heading">
            <div>
              <h1>Threat Intelligence Overview</h1>
              <p>
                Monitor indicators, analyze threats and investigate
                suspicious activity.
              </p>
            </div>

            <div className="period-control">
              {availablePeriods.map((item) => (
                <button
                  key={item.value}
                  className={period === item.value ? "selected" : ""}
                  onClick={() => setPeriod(item.value)}
                >
                  {item.label}
                </button>
              ))}

              <span className="api-status">
                <i /> API DATA
              </span>
            </div>
          </div>

          {error && <div className="error-banner">{error}</div>}

          {loading && (
            <div className="loading-line">
              Refreshing threat intelligence...
            </div>
          )}

          <form className="search-panel" onSubmit={runSearch}>
            <div className="search-intro">
              <span className="search-symbol">⌕</span>
              <div>
                <strong>IOC Investigation</strong>
                <small>Search an IP address, domain or hash</small>
              </div>
            </div>

            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Enter IP, domain or hash..."
            />

            <button type="submit" className="primary-button">
              Investigate <span>→</span>
            </button>
          </form>

          {searchResult && (
            <div className="result-panel">
              <strong>Investigation result</strong>
              <pre>{JSON.stringify(searchResult, null, 2)}</pre>
            </div>
          )}

          <div className="section-title">
            <span className="shield">◇</span>
            <h2>Threat Severity</h2>
            <small>Severity distribution among the loaded indicators</small>
          </div>

          <div className="severity-grid">
            {severityRows.map((item) => (
              <div
                className={`severity-card ${item.className}`}
                key={item.label}
              >
                <div className="severity-icon">{item.icon}</div>
                <div>
                  <h3>{item.label}</h3>
                  <strong>{prettyNumber(item.value)}</strong>
                  <small>Threat indicators</small>
                </div>
                <div className="sparkline">↗↗</div>
              </div>
            ))}
          </div>

          <div className="analytics-grid" id="analytics">
            <section className="panel country-panel">
              <div className="panel-heading">
                <div>
                  <h2><span>◎</span> Top Attack Source Countries</h2>
                  <p>Source distribution</p>
                </div>
                <b>
                  {period === "1" ? "24 HOURS" : `LAST ${period} DAYS`}
                </b>
              </div>

              <div className="country-content">
                <div className="map-wrap">
                 <ThreatMap
                    countries={mapStats?.countries || []}
                    period={mapStats?.period_days || 30}
                  />
                </div>

                <div className="country-chart">
                  <ResponsiveContainer width="100%" height={270}>
                    <BarChart
                      data={countryData.slice(0, 8)}
                      layout="vertical"
                      margin={{ left: 4, right: 18 }}
                    >
                      <CartesianGrid stroke="#18345b" horizontal={false} />
                      <XAxis
                        type="number"
                        stroke="#8caed7"
                        tick={{ fill: "#8caed7", fontSize: 11 }}
                      />
                      <YAxis
                        dataKey="name"
                        type="category"
                        width={58}
                        stroke="#8caed7"
                        tick={{ fill: "#d5e7ff", fontSize: 12 }}
                      />
                      <Tooltip
                        contentStyle={{
                          background: "#071a36",
                          border: "1px solid #1d5b9e",
                          borderRadius: 8,
                          color: "#fff"
                        }}
                      />
                      <Bar
                        dataKey="count"
                        fill="#08a9ff"
                        radius={[0, 6, 6, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="map-legend">
                <span className="red-dot" /> High
                <span className="orange-dot" /> Medium
                <span className="blue-dot" /> Low
              </div>
            </section>

            <section className="panel trends-panel">
              <div className="panel-heading">
                <div>
                  <h2><span>↗</span> Malware Trends</h2>
                  <p>Indicator activity by malware family over time</p>
                </div>
                <b>
                  {period === "1" ? "24 HOURS" : `LAST ${period} DAYS`}
                </b>
              </div>

              <ResponsiveContainer width="100%" height={320}>
                <LineChart
                  data={malwareData}
                  margin={{ top: 18, right: 8, left: 0, bottom: 10 }}
                >
                  <CartesianGrid stroke="#17345c" />
                  <XAxis
                    dataKey="date"
                    stroke="#8caed7"
                    tick={{ fill: "#b9d2f2", fontSize: 11 }}
                  />
                  <YAxis
                    allowDecimals={false}
                    stroke="#8caed7"
                    tick={{ fill: "#b9d2f2", fontSize: 11 }}
                  />
                  <Tooltip
                    contentStyle={{
                      background: "#071a36",
                      border: "1px solid #1d5b9e",
                      borderRadius: 8,
                      color: "#fff"
                    }}
                  />
                  <Legend
                    wrapperStyle={{ color: "#c8ddf7", fontSize: 11 }}
                  />
                  {malwareFamilies.map((family, index) => (
                    <Line
                      key={family}
                      type="monotone"
                      dataKey={family}
                      name={family}
                      stroke={CHART_COLORS[index]}
                      strokeWidth={2.5}
                      dot={false}
                      connectNulls
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>

              {!malwareData.length && (
                <p className="empty-row">
                  No malware trend data is available for this period.
                </p>
              )}
            </section>
          </div>

          <section className="panel indicators-panel" id="indicators">
            <div className="panel-heading">
              <div>
                <h2>Recent Threat Indicators</h2>
                <p>
                  Latest indicators detected across connected intelligence feeds
                </p>
              </div>
              <span className="live-tag"><i /> LIVE FEED</span>
            </div>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    {Object.entries(SORT_FIELDS).map(([label, field]) => (
                      <th
                        key={label}
                        onClick={() => changeSort(field)}
                        title={`Sort by ${label}`}
                        style={{ cursor: "pointer" }}
                      >
                        {label}{" "}
                        {sort === field
                          ? order === "desc" ? "↓" : "↑"
                          : "↕"}
                      </th>
                    ))}
                    <th>Malware</th>
                    <th>Country</th>
                  </tr>
                </thead>

                <tbody>
                  {iocs.map((item, index) => (
                    <tr key={item.id || `${item.value}-${index}`}>
                      <td className="ioc-value">{item.value || "—"}</td>
                      <td>{item.type || item.ioc_type || "—"}</td>
                      <td>{item.source || "—"}</td>
                      <td>
                        <span
                          className={`severity-tag ${
                            (item.severity || 0) >= 3
                              ? "tag-high"
                              : (item.severity || 0) === 2
                              ? "tag-medium"
                              : "tag-low"
                          }`}
                        >
                          {item.severity ?? "—"}
                        </span>
                      </td>
                      <td>
                        {item.seen
                          ? new Date(item.seen).toLocaleString()
                          : item.first_seen
                          ? new Date(item.first_seen).toLocaleString()
                          : "—"}
                      </td>
                      <td>{item.malware || item.malware_family || "—"}</td>
                      <td>{item.country || "Unknown"}</td>
                    </tr>
                  ))}

                  {!iocs.length && (
                    <tr>
                      <td colSpan="7" className="empty-row">
                        No indicators found for this time window.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>

          <section className="panel account-panel" id="account">
            <div className="panel-heading">
              <div>
                <h2>Account & API access</h2>
                <p>Connect your account to use tier-based intelligence access.</p>
              </div>
            </div>

            <div className="account-grid">
              <label>
                API key
                <input
                type="password"
                  value={apiKey}
                  onChange={(event) => saveApiKey(event.target.value)}
                  placeholder="Paste your API key"
                />
              </label>

              <form onSubmit={register} className="register-form">
                <input
                  type="email"
                  required
                  value={registerEmail}
                  onChange={(event) => setRegisterEmail(event.target.value)}
                  placeholder="Email address"
                />
                <input
                  value={industry}
                  onChange={(event) => setIndustry(event.target.value)}
                  placeholder="Industry (e.g. Technology)"
                />
                <input
                  value={domain}
                  onChange={(event) => setDomain(event.target.value)}
                  placeholder="Your domain (e.g. example.com)"
                />
                <button className="primary-button">Register account</button>
              </form>
            </div>

            {registerResult && (
              <p className="success-message">
                Account registered. Save your API key securely.
              </p>
            )}
          </section>
        </section>
      </main>
    </div>
  );
}
