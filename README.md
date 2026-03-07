# CodeForge - NIFTY Options Analytics Platform

[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-19-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688.svg)](https://fastapi.tiangolo.com/)

A comprehensive **real-time options market analytics platform** for NIFTY index options, combining advanced **AI/ML-driven pattern detection**, **volatility analysis**, and **interactive visualizations** to provide actionable trading insights.

---

## 🚀 Key Features

### 📊 Advanced Analytics
- **AI-Powered Anomaly Detection**: Isolation Forest model identifies unusual trading patterns with 5% contamination threshold across 9 engineered features
- **Volume & OI Spike Detection**: Z-score based statistical detection with configurable thresholds (default: 2.5σ)
- **Volatility Pattern Recognition**: Automatic smile and skew detection using polynomial regression analysis
- **KMeans Activity Clustering**: 4-cluster segmentation (High Activity, Moderate, Extreme, Low) identifying institutional positioning

### 📈 Real-Time Market Intelligence
- **Put-Call Ratio (PCR) Analysis**: Sentiment detection with dynamic thresholds
- **Max Pain Calculation**: Automated strike identification where most options expire worthless
- **Support & Resistance Levels**: OI-based key level identification (>1M contracts threshold)
- **Greeks Visualization**: Delta, Gamma, Theta, Vega tracking across strikes

### 🎨 Interactive Visualizations
- **Open Interest Distribution**: Side-by-side Call/Put OI comparison with responsive charts
- **Volatility Smile & Skew**: Real-time IV surface plotting across strikes
- **Volume Heatmaps**: Time × Strike interactive grids powered by Recharts
- **Cumulative OI Timeseries**: Intraday OI flow tracking
- **3D Volatility Surface**: Strike × Expiry × IV visualization

### 🤖 AI-Driven Insights
- Sentiment shift detection (bullish/bearish momentum)
- Institutional activity alerts (extreme volume clusters)
- Volatility surge warnings (z-score > 2.5)
- Support/resistance recommendations based on OI concentration

---

## 🛠️ Technology Stack

### Backend
- **Python 3.13.5**: Core language
- **FastAPI 0.135.1**: High-performance REST API framework
- **DuckDB**: Columnar in-memory database for fast analytics
- **Pandas & NumPy**: Data processing and numerical computing
- **Scikit-learn**: ML models (Isolation Forest, KMeans)
- **SciPy**: Statistical computations and optimization
- **Black-Scholes Model**: Implied volatility calculation

### Frontend
- **React 19**: Modern UI framework with hooks
- **Vite 7.3.1**: Lightning-fast build tool
- **TailwindCSS**: Utility-first styling
- **Recharts**: SVG-based charting library
- **Framer Motion**: Smooth animations
- **Axios**: HTTP client with interceptors

### Data
- **3 CSV files**: NIFTY options data (Feb 17, 24, Mar 02 - 2026)
- **123,115 rows**: Total data points after preprocessing
- **48 columns**: 30+ engineered features
- **Formats**: Parquet, CSV, DuckDB native

---

## 📦 Installation & Setup

### Prerequisites
- **Python 3.11+** (tested on 3.13.5)
- **Node.js 18+** (for frontend)
- **Git**

### Backend Setup

```bash
# 1. Clone repository
git clone https://github.com/yourusername/codeforge.git
cd codeforge/Backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run backend server
python -m uvicorn api:app --reload --port 8000
```

**Backend will start on**: `http://localhost:8000`
- Health check: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
# 1. Navigate to frontend
cd ../frontend

# 2. Install dependencies
npm install

# 3. Configure backend URL (create .env file)
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env

# 4. Run development server
npm run dev
```

**Frontend will start on**: `http://localhost:5173`

---

## 📁 Project Structure

```
codeforge/
├── Backend/
│   ├── api.py                   # FastAPI REST endpoints (21 routes)
│   ├── app.py                   # Streamlit dashboard (deprecated)
│   ├── config.py                # Configuration settings
│   ├── requirements.txt         # Python dependencies
│   ├── data/                    # CSV data files
│   │   ├── 2026-02-17_exp.csv   # 41,041 rows
│   │   ├── 2026-02-24_exp.csv   # 41,037 rows
│   │   └── 2026-03-02_exp.csv   # 41,037 rows
│   └── src/
│       ├── data_loader.py       # CSV ingestion & DuckDB persistence
│       ├── preprocessing.py     # Data cleaning & validation
│       ├── feature_engineering.py # 30+ feature generation
│       ├── analytics.py         # ML models & pattern detection
│       └── visualizations.py    # Plotly chart generation
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── HomePage.jsx     # Landing page
│   │   │   └── Dashboard.jsx    # Main analytics dashboard
│   │   ├── components/
│   │   │   ├── layout/          # Header, Sidebar
│   │   │   ├── charts/          # 8 chart components
│   │   │   ├── MetricCard.jsx
│   │   │   ├── InsightsPanel.jsx
│   │   │   └── Heatmap.jsx
│   │   └── services/
│   │       └── api.js           # Axios API client
│   ├── vite.config.js           # Vite configuration
│   ├── tailwind.config.js       # TailwindCSS setup
│   └── package.json
│
└── README.md                    # This file
```

---

## 🔌 API Endpoints

### Health & Data
- `GET /health` - System health check
- `GET /api/summary` - Dataset summary statistics
- `GET /api/expiries` - Available expiry dates
- `GET /api/data` - Raw data export

### Market Data
- `GET /api/spot-price` - Current NIFTY spot price
- `GET /api/key-metrics` - Dashboard KPIs (spot, ATM, PCR, volume, anomalies)
- `GET /api/pcr` - Put-Call Ratio timeseries

### Analytics
- `GET /api/oi-distribution` - Open Interest by strike
- `GET /api/volume-profile` - Intraday volume distribution
- `GET /api/oi-heatmap` - Volume × Strike × Time heatmap
- `GET /api/max-pain` - Max Pain strike calculation

### Volatility
- `GET /api/volatility-smile` - IV smile curve
- `GET /api/greeks` - Options Greeks
- `GET /api/volatility-surface` - 3D IV surface

### AI/ML
- `GET /api/anomalies` - Top N anomalous data points
- `GET /api/anomaly-scatter` - Anomaly scatter plot data
- `GET /api/volume-spikes` - Detected volume spikes
- `GET /api/ai-insights` - AI-generated trading insights
- `GET /api/pattern-analysis` - Volatility pattern detection

**Query Parameters**: `?expiry=2026-02-17&n=50`

---

## 🧠 Machine Learning Models

### 1. Isolation Forest (Anomaly Detection)
```python
IsolationForest(
    n_estimators=100,
    contamination=0.05,  # 5% expected anomalies
    max_samples='auto',
    random_state=42
)
```
**Features Used (9)**:
- log_volume_CE, log_volume_PE, log_oi_CE, log_oi_PE
- iv_CE, iv_PE
- pcr_volume, pcr_oi
- oi_total

**Output**: 6,156 anomalies detected (5.0% of dataset)

### 2. KMeans Clustering (Activity Segmentation)
```python
KMeans(
    n_clusters=4,
    n_init=10,
    random_state=42
)
```
**Features Used (5)**:
- volume_CE, volume_PE
- oi_CE, oi_PE
- total_volume

**Cluster Distribution**:
- **High Activity**: 53,987 rows
- **Moderate**: 50,145 rows
- **Extreme**: 18,978 rows
- **Low**: 5 rows

### 3. Statistical Detectors
- **Volume Spikes**: Z-score > 2.5 → 4,245 detected
- **OI Change**: Z-score > 2.0 → 5,632 detected
- **IV Spikes**: Z-score > 2.0 → Top 30 returned

---

## 📊 Data Processing Pipeline

```
CSV Files (123,115 rows)
    ↓
[1] Data Loading (DuckDB)
    ├─ Handle missing values
    ├─ Type conversions
    └─ Timestamp parsing
    ↓
[2] Preprocessing
    ├─ Remove duplicates
    ├─ Filter invalid strikes
    ├─ Normalize timestamps
    └─ Outlier capping
    ↓
[3] Feature Engineering
    ├─ Financial metrics (PCR, Greeks)
    ├─ Log transformations
    ├─ Time-based features
    └─ Implied Volatility (Black-Scholes)
    ↓
[4] Analytics Pipeline
    ├─ Isolation Forest
    ├─ KMeans Clustering
    ├─ Volume/OI spike detection
    └─ Volatility pattern analysis
    ↓
[5] API Serving (FastAPI)
    └─ Cached results (<1ms response)
```

---

## 🎯 Use Cases

### For Retail Traders
- Identify support/resistance levels based on OI concentration
- Detect unusual institutional activity via anomaly alerts
- Time entries using volume spike signals
- Monitor market sentiment shifts via PCR

### For Quantitative Analysts
- Volatility smile/skew arbitrage opportunities
- Max Pain-based expiry drift predictions
- Greeks-based delta-neutral strategies
- Backtesting using historical data exports

### For Market Researchers
- Intraday OI flow analysis
- Cross-strike volatility correlations
- Time-decay patterns (Theta analysis)
- Volume-weighted average strike calculations

---

## ⚡ Performance Optimizations

### Backend
- **In-memory caching**: Analytics computed once on startup
- **DuckDB columnar storage**: 10x faster aggregations vs row-based
- **Vectorized operations**: NumPy/Pandas for batch processing
- **Async FastAPI**: Non-blocking I/O for concurrent requests

### Frontend
- **Code splitting**: Route-based lazy loading
- **Memoization**: React.useMemo for expensive calculations
- **Virtual scrolling**: Large dataset rendering optimization
- **Debounced filters**: Reduce API call frequency

---

## 🔧 Configuration

### Backend (`Backend/config.py`)
```python
DATA_DIR = "data/"
DB_PATH = "data/options.duckdb"
IV_SAMPLE_FRAC = 0.05  # IV calculation sample rate
ANOMALY_CONTAMINATION = 0.05
KMEANS_N_CLUSTERS = 4
VOLUME_SPIKE_THRESHOLD = 2.5
```

### Frontend (`.env`)
```bash
VITE_API_BASE_URL=http://localhost:8000/api
```

---

## 📝 Development Workflow

### Adding New Features

1. **Backend**:
   ```bash
   # Add feature to analytics.py
   # Add endpoint in api.py
   # Test: http://localhost:8000/docs
   ```

2. **Frontend**:
   ```bash
   # Create component in src/components/
   # Add to Dashboard.jsx
   # Test: npm run dev
   ```

### Running Tests
```bash
# Backend
cd Backend
python -m pytest tests/

# Frontend
cd frontend
npm test
```

### Building for Production
```bash
# Backend
pip install -r requirements.txt
python -m uvicorn api:app --host 0.0.0.0 --port 8000

# Frontend
npm run build
npm run preview  # Test production build
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check port availability
netstat -an | findstr :8000
```

### Frontend won't connect to backend
```bash
# Verify .env file
cat frontend/.env  # Should have VITE_API_BASE_URL=http://localhost:8000/api

# Check backend health
curl http://localhost:8000/health

# Hard refresh browser
Ctrl + Shift + R
```

### Data not loading
```bash
# Verify CSV files exist
ls Backend/data/*.csv

# Check data loading logs
# Look for "[Data]" prefixed messages in terminal
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

**Code Style**:
- Python: Black formatter (line length 100)
- JavaScript: ESLint + Prettier
- Commits: Conventional Commits format

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👤 Author

**Ashish**

---

## 🙏 Acknowledgments

- NIFTY options data sourced from public market feeds
- Inspired by professional trading platforms like Opstra and Sensibull
- Built with modern open-source technologies (FastAPI, React, DuckDB)
- Special thanks to the Python and React communities

---

## 📞 Support

For issues and questions, feel free to reach out.

---

**⭐ Star this repo if you find it useful!**

Last Updated: March 7, 2026
