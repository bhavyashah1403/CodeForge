# API Documentation — For React Frontend

## Quick Start

```bash
# Backend (Python) — run from project root
cd codeforge
.\venv\Scripts\activate
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

- **API Base URL:** `http://localhost:8000`
- **Swagger Docs (auto):** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

CORS is enabled for all origins — React dev server (`localhost:3000`) will work out of the box.

---

## Endpoints

### Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check, returns `{ status, message, rows }` |
| GET | `/health` | Detailed health status |

### Data

| Method | Endpoint | Params | Description |
|--------|----------|--------|-------------|
| GET | `/api/summary` | — | Dataset summary (rows, columns, date range, strikes) |
| GET | `/api/expiries` | — | List of expiry dates `["2026-02-17", ...]` |
| GET | `/api/timestamps` | `?expiry=2026-02-17&limit=100` | Available timestamps for an expiry |
| GET | `/api/data` | `?expiry=&strike=&page=1&page_size=100` | Paginated raw data |

### Market Data

| Method | Endpoint | Params | Description |
|--------|----------|--------|-------------|
| GET | `/api/spot-price` | `?expiry=` | Spot price timeseries |
| GET | `/api/key-metrics` | `?expiry=` | Dashboard header cards (spot, ATM, PCR, OI, sentiment) |

### Analytics

| Method | Endpoint | Params | Description |
|--------|----------|--------|-------------|
| GET | `/api/oi-distribution` | `?timestamp=&expiry=` | OI per strike (for bar chart) |
| GET | `/api/oi-heatmap` | `?oi_type=oi_CE&expiry=` | OI matrix: strikes × timestamps |
| GET | `/api/volume-profile` | `?expiry=` | Volume per strike |
| GET | `/api/pcr` | — | Put-Call Ratio timeseries with spot |
| GET | `/api/max-pain` | `?timestamp=&expiry=` | Max Pain strike calculation |

### Volatility

| Method | Endpoint | Params | Description |
|--------|----------|--------|-------------|
| GET | `/api/volatility-smile` | `?timestamp=&expiry=` | IV across strikes (smile curve) |
| GET | `/api/greeks` | `?timestamp=&expiry=` | Delta, Gamma, Theta, Vega per strike |

### AI / ML

| Method | Endpoint | Params | Description |
|--------|----------|--------|-------------|
| GET | `/api/anomalies` | `?n=50&expiry=` | Top N anomalies (Isolation Forest) |
| GET | `/api/anomaly-scatter` | `?expiry=` | All points with anomaly flag (for scatter) |
| GET | `/api/volume-spikes` | `?n=50&expiry=` | Top N volume spikes |

### Evaluation

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/metrics` | Full evaluation metrics (silhouette score, rates, etc.) |

---

## Response Formats

### Key Metrics (`/api/key-metrics`)
```json
{
  "spot_price": 25459.35,
  "atm_strike": 25450.0,
  "pcr_oi": 3.6094,
  "total_oi": 38564825,
  "total_volume": 21125,
  "anomalies_count": 6156,
  "volume_spikes": 4245,
  "sentiment": "Bullish"
}
```

### OI Distribution (`/api/oi-distribution`)
```json
[
  { "strike": 23100, "oi_CE": 130, "oi_PE": 2533115, "volume_CE": 65, "volume_PE": 9945, "total_oi": 2533245 },
  { "strike": 23200, "oi_CE": 65, "oi_PE": 711815, ... }
]
```

### PCR Timeseries (`/api/pcr`)
```json
[
  { "datetime": "2026-02-10 09:15:00", "total_oi_CE": 1234, "total_oi_PE": 5678, "pcr_oi": 4.6, "pcr_volume": 2.1, "spot": 25933.3 }
]
```

### Anomalies (`/api/anomalies`)
```json
[
  { "datetime": "2026-02-16 10:12:00", "strike": 25500, "CE": 137.5, "PE": 85.6, "spot_close": 25487.2, "anomaly_score": -0.2268 }
]
```

### Volatility Smile (`/api/volatility-smile`)
```json
[
  { "strike": 24000, "iv_CE": 0.25, "iv_PE": 0.28, "iv_CE_pct": 25.0, "iv_PE_pct": 28.0, "moneyness_label": "OTM" }
]
```

### OI Heatmap (`/api/oi-heatmap`)
```json
{
  "strikes": [23100, 23150, ...],
  "timestamps": ["2026-02-10 09:15:00", ...],
  "values": [[0, 130, ...], [65, 0, ...]]
}
```

---

## React Integration Example

```jsx
// src/hooks/useApi.js
const API_BASE = 'http://localhost:8000';

export const fetchKeyMetrics = async (expiry) => {
  const url = expiry 
    ? `${API_BASE}/api/key-metrics?expiry=${expiry}` 
    : `${API_BASE}/api/key-metrics`;
  const res = await fetch(url);
  return res.json();
};

export const fetchOIDistribution = async (expiry, timestamp) => {
  const params = new URLSearchParams();
  if (expiry) params.append('expiry', expiry);
  if (timestamp) params.append('timestamp', timestamp);
  const res = await fetch(`${API_BASE}/api/oi-distribution?${params}`);
  return res.json();
};

export const fetchAnomalies = async (n = 50, expiry) => {
  const params = new URLSearchParams({ n });
  if (expiry) params.append('expiry', expiry);
  const res = await fetch(`${API_BASE}/api/anomalies?${params}`);
  return res.json();
};
```

```jsx
// src/components/Dashboard.jsx
import { useEffect, useState } from 'react';
import { fetchKeyMetrics } from '../hooks/useApi';

function Dashboard({ expiry }) {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    fetchKeyMetrics(expiry).then(setMetrics);
  }, [expiry]);

  if (!metrics) return <div>Loading...</div>;

  return (
    <div className="grid grid-cols-4 gap-4">
      <Card title="Spot Price" value={`₹${metrics.spot_price}`} />
      <Card title="PCR (OI)" value={metrics.pcr_oi} />
      <Card title="Sentiment" value={metrics.sentiment} />
      <Card title="Anomalies" value={metrics.anomalies_count} />
    </div>
  );
}
```

---

## Tech Stack (FOSS)

| Layer | Technology | Role |
|-------|-----------|------|
| Database | DuckDB | Serverless analytical DB |
| Data Processing | Pandas, NumPy | DataFrames, math |
| ML/AI | Scikit-learn (Isolation Forest) | Anomaly detection |
| IV Calculation | Black-Scholes + Newton-Raphson | Implied Volatility |
| API | FastAPI + Uvicorn | REST API server |
| Frontend | React (your part) | Dashboard UI |
