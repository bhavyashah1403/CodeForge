# CodeForge: AI-Powered Options Market Analytics Platform

**Team:** CodeForge  
**Date:** March 2026

---

## 1. Introduction

When we first looked at the raw options chain CSVs, the immediate challenge was clear — each file had tens of thousands of rows across dozens of columns, and making sense of what's actually happening in the market from that raw dump is nearly impossible by eye. Strike-level OI, volume, premiums, timestamps — it's all there, but none of it is actionable without serious processing.

Our goal with CodeForge was to build a system that takes this raw NIFTY options data and turns it into something a trader or analyst can actually use: computed Greeks, implied volatility, anomaly flags, sentiment indicators, and interactive charts — all served through a clean web dashboard backed by a REST API.

The core objectives were:
- Ingest multi-day options CSVs and standardize them into a clean analytical dataset.
- Compute options-specific features (IV via Black-Scholes, Greeks, PCR, moneyness, etc.).
- Run unsupervised ML (Isolation Forest) to flag unusual market behavior without needing labeled data.
- Cluster strike-level activity using KMeans to expose structural patterns across strikes.
- Serve everything through a FastAPI backend with 21 REST endpoints.
- Visualize it all in a React dashboard with Recharts — OI distribution, volatility smile, PCR timeseries, anomaly scatter, heatmaps, and more.

We wanted every piece to be modular. If someone wants to swap out the anomaly detector or plug in live data, the pipeline should support that without rewriting the whole thing.

## 2. Dataset Understanding

### 2.1 Data Source

We worked with three NIFTY options chain CSV snapshots:

| File | Expiry Date |
|------|-------------|
| `2026-02-17_exp.csv` | Feb 17, 2026 |
| `2026-02-24_exp.csv` | Feb 24, 2026 |
| `2026-03-02_exp.csv` | Mar 02, 2026 |

Combined, we're looking at **~123,000 rows × 48 columns** after feature engineering. Each row represents one (strike, expiry, timestamp) observation with Call/Put premiums, OI, volume, and spot price.

### 2.2 Preprocessing Pipeline

The preprocessing runs through `src/preprocessing.py` in a defined sequence:

1. **Schema Validation** — We first check that all 12 required columns (`symbol`, `datetime`, `expiry`, `CE`, `PE`, `spot_close`, `ATM`, `strike`, `oi_CE`, `oi_PE`, `volume_CE`, `volume_PE`) are present and correctly typed. If anything is missing, the pipeline fails early rather than producing garbage downstream.

2. **Missing Value Handling** — Rows where critical price columns (`CE`, `PE`, `spot_close`, `strike`) are null get dropped entirely. For OI and volume columns, nulls are filled with 0 since missing activity is semantically zero activity.

3. **Duplicate Removal** — Duplicates keyed on `(datetime, expiry, strike)` are removed, keeping the last entry.

4. **Invalid Data Filtering** — We enforce business rules: option prices >= 0, spot > 0, strike > 0, OI and volume >= 0. Anything violating these constraints gets dropped.

5. **Derived Column Generation** — We compute 13 base derived features:
   - **Moneyness** = spot / strike, with categorical labels (ITM/ATM/OTM using 0.97–1.03 boundary)
   - **Time to expiry** in both days and years (needed for BS model)
   - **Intrinsic & extrinsic value** for both CE and PE
   - **Put-Call Ratio** by OI and by volume
   - **Total OI** and **total volume** (CE + PE combined)
   - **Distance from ATM** in strike points

### 2.3 Feature Engineering

The feature engineering layer (`src/feature_engineering.py`) adds the quantitative finance features:

**Implied Volatility** — We compute IV using Newton-Raphson iteration on the Black-Scholes pricing formula. For each option, the solver starts at sigma = 0.3 and iterates until the BS model price matches the observed market price within tolerance (1e-6) or hits 100 iterations. The Vega drives each Newton step. Computing IV for all ~123K rows would be extremely slow (it's row-by-row), so we support sampling — in practice we compute on a 10% sample and merge back via `(datetime, strike, expiry)` join.

**Greeks** — We compute Delta, Gamma, Theta, and Vega analytically from the BS formula using the computed IV as input. Where IV is unavailable, we fall back to sigma = 0.2. All four Greeks are computed for both calls and puts using vectorized NumPy operations — no per-row loops for this part.

**Volatility Smile Metrics** — IV spread (CE - PE) and relative strike (normalized distance from ATM) are computed for downstream smile/skew fitting.

**Volume/OI Change Features** — Rolling 5-period moving averages for volume, OI period-over-period deltas, and volume-to-MA ratios (useful for spike detection) are calculated per (strike, expiry) group.

After the full pipeline, each row carries ~48 features — the original 12 columns plus 36 derived features.

## 3. Proposed Approach and Methodology

### 3.1 System Architecture

```
CSV Files --> Data Loader (DuckDB + Pandas)
          --> Preprocessing Pipeline
          --> Feature Engineering (IV, Greeks, PCR, ...)
          --> Analytics Pipeline (Isolation Forest, KMeans, Z-score)
          --> FastAPI REST API (21 endpoints)
          --> React Dashboard (Recharts, TailwindCSS)
```

The architecture follows a clear separation:

- **Ingestion**: `data_loader.py` discovers all CSVs in `/data`, loads them into Pandas DataFrames, and persists to DuckDB (a serverless columnar database) for potential SQL-based analytics later.
- **Processing**: `preprocessing.py` and `feature_engineering.py` transform raw data into analysis-ready features.
- **Analytics**: `analytics.py` runs ML models and statistical detectors.
- **Serving**: `api.py` (FastAPI) exposes everything as JSON endpoints. Frontend consumes these via Axios.
- **Visualization**: React + Recharts renders the interactive dashboard.

All data processing happens once at server startup and is cached in memory, so API responses are essentially instant — no re-computation per request.

### 3.2 AI/ML Components

#### Isolation Forest (Anomaly Detection)

We use scikit-learn's `IsolationForest` with 100 estimators and 5% contamination rate. The model takes 9 features as input: CE price, PE price, OI for both sides, volume for both sides, total OI, total volume, and PCR (OI-based).

Why Isolation Forest? We don't have labeled anomaly data — that rules out supervised approaches entirely. Isolation Forest works by randomly partitioning the feature space. The idea is that anomalies are "easier to isolate" (they need fewer random splits) than normal points. It gives us both a binary label (anomaly/not) and a continuous anomaly score (how isolated the point is), which lets us rank the most unusual observations rather than just getting a yes/no flag.

The feature matrix is standardized using `StandardScaler` before fitting. NaN rows are excluded from training, and predictions are mapped back to the full DataFrame.

#### KMeans Clustering (Activity Patterns)

We run KMeans with k=4 on (total_oi, total_volume, pcr_oi, CE, PE) to discover natural groupings in market activity. After clustering, we label each cluster by ranking their mean total volume: "Low Activity", "Moderate Activity", "High Activity", "Extreme Activity".

This gives us insight into which strikes are seeing speculative action vs. quiet hedging — something you really can't see from raw numbers alone.

#### Z-Score Detectors

For volume spike detection, we compute z-scores within each (strike, expiry) group. Any observation with z > 3.0 (configurable) is flagged as a spike. Same approach for OI changes, with threshold at 2.0.

These are simpler than Isolation Forest but complementary — IF catches complex multi-dimensional anomalies, while z-score detectors catch obvious univariate extremes. When we looked at the cross-validation (overlap between IF anomalies and volume spikes), the agreement was meaningful — points flagged by both methods tend to be the most actionable signals.

#### Volatility Pattern Detection

We detect two key options phenomena:
- **Skew**: Compare mean OTM put IV vs. mean OTM call IV. Ratio > 1.1 means put skew (crash protection demand), < 0.9 means call skew. OTM is defined as strikes 2%+ away from ATM.
- **Smile**: Fit a quadratic curve (`np.polyfit`, degree 2) to IV vs. relative strike. A positive quadratic coefficient > 0.05 indicates a volatility smile.

We also detect IV spikes by computing z-scores on IV changes across consecutive timestamps per strike.

### 3.3 AI Insight Generation

The insight engine (`generate_ai_insights`) combines outputs from all the models into structured, actionable alerts:

1. **Sentiment Shift** — If PCR moves by > 0.1 between timestamps, alert with direction and magnitude.
2. **Anomaly Hotspots** — Identify top anomalous strikes from Isolation Forest output.
3. **Volume Spike Alerts** — Surface locations with CE/PE volume breakdown.
4. **Max Pain Analysis** — Strike where option writers' total losses are minimized, and its distance from current spot.
5. **Support/Resistance from OI** — Strikes with highest Call OI (resistance) and Put OI (support).
6. **Volatility Skew Alerts** — Report skew direction with OTM put/call IV averages.

Each insight gets a severity level (high/medium/low) and timestamp. The dashboard presents them sorted by importance.

### 3.4 Evaluation Metrics

We compute quantitative metrics to assess the platform's outputs:

- **Data Quality**: Null percentage, duplicate rate, completeness score.
- **Anomaly Detection**: Count, rate, mean/std/median anomaly scores, plus silhouette score (separation quality between normal and anomalous clusters, computed on standardized features, sampled up to 5,000 points).
- **Volume/OI Detection**: Spike counts and rates for both detectors.
- **IV Metrics**: Coverage percentage, mean IV for CE/PE, standard deviations.
- **Feature Coverage**: How many of the 29 expected derived features are present.
- **Cross-Validation**: Overlap between Isolation Forest anomalies and volume spikes, measuring agreement between independent detection methods.

## 4. Uniqueness and Innovation

### What makes CodeForge different from a generic analytics dashboard:

**Domain-aware feature engineering.** We don't just throw raw columns at an ML model. Features like IV (Newton-Raphson BS solver), Greeks (analytical BS formulas), moneyness categories, PCR, intrinsic/extrinsic values — these are quantitative finance constructs that make the analytics meaningful to options traders specifically.

**Hybrid detection strategy.** Isolation Forest handles complex multi-dimensional anomalies that simple thresholds miss. Z-score detectors handle obvious univariate spikes. KMeans reveals structural patterns. Using all three gives a richer picture than any single method.

**Volatility structure analysis.** Smile curvature via quadratic fitting, skew ratios, IV term structure across expiries — these directly answer questions like "is the market pricing in crash risk?" or "do near-term and far-term options disagree on volatility?".

**Insight generation layer.** Instead of making users interpret raw model outputs, the system synthesizes results into natural-language alerts with severity classification. This bridges the gap between ML outputs and actionable intelligence.

**Startup-cached processing.** All heavy computation (IV, Greeks, ML models) runs once at startup. API responses are sub-millisecond lookups, not re-computations. This is critical for interactive dashboards where lag kills usability.

**Full FOSS stack.** Every component is open-source: Python, Pandas, NumPy, scikit-learn, SciPy, FastAPI, DuckDB, React, Recharts, TailwindCSS, Vite, Framer Motion. No proprietary tools, no paid APIs, fully reproducible.

## 5. Implementation Details

### 5.1 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Data Loading | Pandas + DuckDB | DataFrame manipulation + columnar storage |
| Preprocessing | Pandas + NumPy | Vectorized cleaning and derivation |
| Feature Eng. | SciPy (norm), NumPy | BS model math, analytical Greeks |
| ML/Analytics | scikit-learn | IsolationForest, KMeans, StandardScaler, silhouette_score |
| API | FastAPI + Uvicorn | Async ASGI server, auto OpenAPI docs |
| Frontend | React 19 + Vite 7 | SPA with hot module replacement |
| Charts | Recharts | Composable React charts built on D3 |
| Styling | TailwindCSS 4 | Utility-first CSS, dark theme |
| Animation | Framer Motion | Entry animations for dashboard cards |
| HTTP Client | Axios | API calls with error interceptors |

### 5.2 Backend API Endpoints (21 total)

Organized by function:

- **Data & Health (5):** `/health`, `/api/summary`, `/api/expiries`, `/api/timestamps`, `/api/data` (paginated)
- **Market Data (1):** `/api/spot-price`
- **Analytics (5):** `/api/oi-distribution`, `/api/pcr`, `/api/max-pain`, `/api/volume-profile`, `/api/oi-heatmap`
- **Volatility (3):** `/api/volatility-smile`, `/api/greeks`, `/api/volatility-surface`
- **AI/ML (4):** `/api/anomalies`, `/api/anomaly-scatter`, `/api/volume-spikes`, `/api/pattern-analysis`
- **Intelligence (2):** `/api/ai-insights`, `/api/key-metrics`
- **Evaluation (1):** `/api/metrics`

All endpoints support expiry filtering. Anomalies endpoint supports top-N selection (up to 500). Raw data supports pagination with configurable page size.

### 5.3 Frontend Dashboard

The dashboard is organized into 6 sections:

1. **Market Pulse** — 8 metric cards: spot price, ATM strike, PCR, sentiment, total OI, volume, anomaly count, volume spike count.

2. **OI & Volume Distribution** — Side-by-side bar charts showing trader positioning (OI) and activity concentration (volume) across strikes.

3. **Volatility Analysis** — Volatility smile/skew chart and volatility surface (IV across strikes and expiries). Pattern analysis cards display skew direction, smile curvature, KMeans activity clusters, and IV spike count.

4. **Time Series** — PCR timeseries with spot price overlay (dual Y-axis) and cumulative OI trend. A PCR = 1 reference line helps identify bullish/bearish transitions.

5. **Activity Heatmap** — Strike x time volume heatmap for visualizing when and where trading concentrates.

6. **AI Analytics** — Anomaly scatter plot (normal points in indigo vs. anomalies in red), Greeks distribution across strikes, and AI insight cards with severity-based coloring.

Dynamic features: Sidebar fetches available expiries from the API on mount (with hardcoded fallback), loading spinner during data fetch, and a refresh mechanism using custom browser events.

### 5.4 Key Algorithms

**Newton-Raphson IV Solver:**
- Input: market price, spot (S), strike (K), time-to-expiry (T)
- Initial guess: sigma = 0.3
- Update rule: sigma_new = sigma - (BS_price(sigma) - market_price) / Vega(sigma)
- Convergence: |BS_price - market_price| < 1e-6, or 100 iterations
- Returns NaN for degenerate cases (T <= 0, price below intrinsic)

**Max Pain Calculation:**
- For each candidate strike K, compute total writer losses across all strikes:
  - Pain_CE(K) = sum of max(K - strike_i, 0) * oi_CE_i
  - Pain_PE(K) = sum of max(strike_i - K, 0) * oi_PE_i
- Max Pain = strike that minimizes (Pain_CE + Pain_PE)

## 6. Results and Observations

Running the platform on our 3-file dataset:

**Data Processing:** All 123,000+ rows processed successfully. After preprocessing, rows with expired options or invalid data were filtered out. Feature engineering produced 29 derived features with high coverage for financial features (~100%) and ~10% for IV due to sampling.

**Anomaly Detection:** At 5% contamination, Isolation Forest flagged ~6,000 points as anomalous. The silhouette score showed meaningful separation between anomalous and normal clusters, indicating the model is capturing real structure rather than randomly labeling.

**Clustering:** KMeans segmented data into four distinct activity groups. The "Extreme Activity" cluster had significantly fewer rows but several times the median total volume — likely strikes with institutional-sized positioning.

**Volume Spikes:** Z-score detection found concentrated spikes at near-ATM strikes, which is consistent with where we'd expect the heaviest trading. Cross-validation with Isolation Forest showed notable overlap — points flagged by both are the strongest signals.

**Volatility Patterns:** Skew analysis consistently showed put skew across expiries, which is typical for index options (OTM put IV stays elevated due to crash protection demand). Smile curvature was positive — confirming the U-shaped IV structure.

**Sentiment:** PCR ranged across bullish and neutral territory depending on expiry and timestamp. The insight engine captured PCR shifts accurately, alerting when the ratio crossed thresholds.

**Key Observation:** The most interesting findings came from combining signals. Strikes where anomalies, volume spikes, and OI buildup all coincided were at levels near support/resistance zones identified by max pain and OI distribution — the different models are converging on the same market structure from different angles.

## 7. Discussion

### 7.1 What Worked

The modular pipeline design paid off throughout development. When we added KMeans clustering or volatility pattern detection later, it was just new functions in `analytics.py` and new endpoints in `api.py` — nothing else had to change. Startup-cached processing means adding model complexity doesn't affect response times.

The combination of Isolation Forest + z-score + KMeans gives more robust signals than any single method. Each has blind spots that the others cover.

### 7.2 Limitations

- **No ground truth labels.** We can't compute precision/recall for anomaly detection since there's no labeled "known anomaly" dataset. Silhouette score and cross-validation are proxies, not direct accuracy measures.
- **IV sampling.** Computing IV on 10% sample is a speed tradeoff. Full computation would be more complete but significantly slower. In deployment, this could be pre-computed in batch or parallelized.
- **Batch-only processing.** The entire dataset loads and processes at startup. No streaming or incremental updates — adding new data requires a restart. For a hackathon this is fine, but production would need an ingestion pipeline.
- **Contamination sensitivity.** The 5% parameter directly controls anomaly count. Ideally this should be tuned with domain expert feedback, which we didn't have access to.
- **Single asset.** Only NIFTY currently. The analytics pipeline itself is asset-agnostic, so multi-asset support is mainly a data ingestion change.

### 7.3 Possible Improvements

- Real-time data ingestion via WebSocket or message queue, with incremental model updates.
- Adaptive contamination thresholds that adjust by volatility regime.
- Model persistence (joblib/pickle) to avoid retraining every startup.
- Explainability integration (SHAP or LIME) to surface *why* a point is anomalous, not just *that* it is.
- Multi-asset support (BANKNIFTY, FINNIFTY) when data becomes available.
- User-configurable alerting thresholds in the UI.

## 8. Conclusion and Future Work

CodeForge shows that a meaningful options analytics platform can be built from raw CSV data using entirely open-source tools. The pipeline — from data loading through feature engineering, ML-based detection, and interactive visualization — produces insights that go beyond what simple threshold-based dashboards can offer.

The layered detection approach (Isolation Forest for multi-dimensional anomalies, KMeans for structural patterns, z-score for univariate spikes) gives richer and more reliable signals than any single method alone. The domain-specific feature engineering (IV, Greeks, PCR, moneyness) ensures the analytics are relevant to options markets specifically.

Going forward, the main extension areas are real-time data support, model explainability, and multi-asset coverage. The modular design makes each of these feasible without restructuring the existing system.

## 9. References

[1] F. T. Liu, K. M. Ting, and Z.-H. Zhou, "Isolation Forest," *Proceedings of the 2008 IEEE International Conference on Data Mining*, 2008.
[2] J. C. Hull, *Options, Futures, and Other Derivatives*, 10th ed., Pearson, 2017.
[3] Black, F. and Scholes, M., "The Pricing of Options and Corporate Liabilities," *Journal of Political Economy*, 1973.
[4] scikit-learn Documentation, "IsolationForest," https://scikit-learn.org/
[5] FastAPI Documentation, https://fastapi.tiangolo.com/
[6] DuckDB Documentation, https://duckdb.org/docs/
[7] Recharts Documentation, https://recharts.org/
[8] React Documentation, https://react.dev/
