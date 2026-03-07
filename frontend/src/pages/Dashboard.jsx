import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  DollarSign,
  Target,
  PieChart,
  Activity,
  TrendingUp,
  BarChart3,
  AlertTriangle,
  Zap,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

// Layout
import Sidebar from '../components/layout/Sidebar';
import Header from '../components/layout/Header';

// Components
import MetricCard from '../components/MetricCard';
import ChartCard from '../components/ChartCard';
import InsightsPanel from '../components/InsightsPanel';
import Heatmap from '../components/Heatmap';

// Charts
import OIDistributionChart from '../components/charts/OIDistributionChart';
import VolatilitySmileChart from '../components/charts/VolatilitySmileChart';
import CumulativeOIChart from '../components/charts/CumulativeOIChart';
import AnomalyScatterChart from '../components/charts/AnomalyScatterChart';
import GreeksChart from '../components/charts/GreeksChart';
import PCRTimeseriesChart from '../components/charts/PCRTimeseriesChart';
import VolatilitySurfaceChart from '../components/charts/VolatilitySurfaceChart';
import VolumeProfileChart from '../components/charts/VolumeProfileChart';

// API
import {
  fetchMarketSummary,
  fetchOpenInterest,
  fetchVolatilitySmile,
  fetchVolumeHeatmap,
  fetchAIInsights,
  fetchCumulativeOI,
  fetchAnomalyScatter,
  fetchGreeks,
  fetchVolatilitySurface,
  fetchPatternAnalysis,
} from '../services/api';

// ── Mock Data (used when backend is unavailable) ─────────────────

function generateMockOI() {
  const strikes = [];
  for (let s = 23000; s <= 26000; s += 100) {
    strikes.push({
      strike: s,
      oi_CE: Math.floor(Math.random() * 800000 + 200000),
      oi_PE: Math.floor(Math.random() * 800000 + 200000),
    });
  }
  return strikes;
}

function generateMockVolSmile() {
  const data = [];
  for (let s = 23000; s <= 26000; s += 100) {
    const dist = Math.abs(s - 24500) / 1000;
    data.push({
      strike: s,
      iv_CE_pct: 12 + dist * dist * 1.8 + (Math.random() - 0.5) * 1.5,
      iv_PE_pct: 13 + dist * dist * 2.0 + (Math.random() - 0.5) * 1.5,
    });
  }
  return data;
}

function generateMockHeatmap() {
  const times = [];
  const strikes = [];
  const data = [];

  for (let h = 9; h <= 15; h++) {
    for (let m = 0; m < 60; m += 15) {
      times.push(`${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`);
    }
  }

  for (let s = 24000; s <= 25000; s += 100) {
    strikes.push(s);
  }

  times.forEach((t) => {
    strikes.forEach((s) => {
      data.push({
        time: t,
        strike: s,
        volume: Math.floor(Math.random() * 50000),
      });
    });
  });

  return { data, times, strikes };
}

function generateMockCumulativeOI() {
  const data = [];
  let ceCum = 2000000;
  let peCum = 1800000;
  for (let h = 9; h <= 15; h++) {
    for (let m = 0; m < 60; m += 15) {
      ceCum += Math.floor((Math.random() - 0.45) * 80000);
      peCum += Math.floor((Math.random() - 0.48) * 80000);
      data.push({
        time: `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`,
        cumulative_oi_ce: Math.max(0, ceCum),
        cumulative_oi_pe: Math.max(0, peCum),
      });
    }
  }
  return data;
}

const mockInsights = [
  {
    id: 1,
    type: 'anomaly',
    title: 'Anomaly Detected',
    description:
      'AI model detected unusual market activity. Connect backend to see real-time insights.',
    timestamp: new Date().toLocaleString(),
    severity: 'high',
  },
  {
    id: 2,
    type: 'info',
    title: 'System Ready',
    description:
      'Backend API powers AI-driven insights from anomaly detection, clustering, and volatility analysis.',
    timestamp: new Date().toLocaleString(),
    severity: 'low',
  },
];

// ── Dashboard Page ───────────────────────────────────────────────

export default function Dashboard() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState({
    asset: 'NIFTY',
    expiry: '2026-02-17',
    strikeRange: 25000,
    timeRange: 6,
    showAnomalies: true,
  });

  const [marketData, setMarketData] = useState({
    spotPrice: null,
    atmStrike: null,
    pcr: null,
    totalOI: null,
    totalVolume: null,
    anomaliesCount: 0,
    volumeSpikes: 0,
    sentiment: 'Neutral',
  });

  const [oiData, setOiData] = useState([]);
  const [volSmileData, setVolSmileData] = useState([]);
  const [heatmapState, setHeatmapState] = useState({ data: [], times: [], strikes: [] });
  const [cumulativeOI, setCumulativeOI] = useState([]);
  const [insights, setInsights] = useState([]);
  const [anomalyScatter, setAnomalyScatter] = useState([]);
  const [greeksData, setGreeksData] = useState([]);
  const [volSurface, setVolSurface] = useState([]);
  const [patternData, setPatternData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Format large numbers
  const fmtNum = (v) => {
    if (v == null) return '—';
    if (v >= 1e7) return (v / 1e7).toFixed(2) + ' Cr';
    if (v >= 1e5) return (v / 1e5).toFixed(2) + ' L';
    if (v >= 1e3) return (v / 1e3).toFixed(1) + 'K';
    return Number(v).toLocaleString();
  };

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [summary, oi, volSmile, heatmap, aiInsights, cumOI, scatter, greeks, surface, patterns] =
        await Promise.allSettled([
          fetchMarketSummary(filters),
          fetchOpenInterest(filters),
          fetchVolatilitySmile(filters),
          fetchVolumeHeatmap(filters),
          fetchAIInsights(filters),
          fetchCumulativeOI(filters),
          fetchAnomalyScatter(filters),
          fetchGreeks(filters),
          fetchVolatilitySurface(filters),
          fetchPatternAnalysis(filters),
        ]);

      // Market Summary
      if (summary.status === 'fulfilled' && summary.value) {
        const s = summary.value;
        setMarketData({
          spotPrice: s.spot_price,
          atmStrike: s.atm_strike,
          pcr: s.pcr_oi,
          totalOI: s.total_oi,
          totalVolume: s.total_volume,
          anomaliesCount: s.anomalies_count || 0,
          volumeSpikes: s.volume_spikes || 0,
          sentiment: s.sentiment || 'Neutral',
        });
      }

      // OI Distribution
      setOiData(
        oi.status === 'fulfilled' && Array.isArray(oi.value)
          ? oi.value
          : generateMockOI()
      );

      // Volatility Smile
      setVolSmileData(
        volSmile.status === 'fulfilled' && Array.isArray(volSmile.value)
          ? volSmile.value
          : generateMockVolSmile()
      );

      // Heatmap
      if (heatmap.status === 'fulfilled' && heatmap.value?.strikes) {
        const h = heatmap.value;
        const heatmapData = [];
        h.strikes.forEach((strike, si) => {
          h.timestamps.forEach((ts, ti) => {
            heatmapData.push({
              strike,
              time: new Date(ts).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
              volume: h.values[si]?.[ti] || 0,
            });
          });
        });
        const uniqueTimes = [...new Set(heatmapData.map((d) => d.time))];
        const uniqueStrikes = [...new Set(heatmapData.map((d) => d.strike))];
        setHeatmapState({ data: heatmapData, times: uniqueTimes, strikes: uniqueStrikes });
      } else {
        setHeatmapState(generateMockHeatmap());
      }

      // Cumulative OI / PCR Timeseries
      setCumulativeOI(
        cumOI.status === 'fulfilled' && Array.isArray(cumOI.value)
          ? cumOI.value
          : generateMockCumulativeOI()
      );

      // AI Insights
      setInsights(
        aiInsights.status === 'fulfilled' && Array.isArray(aiInsights.value) && aiInsights.value.length > 0
          ? aiInsights.value
          : mockInsights
      );

      // Anomaly Scatter
      setAnomalyScatter(
        scatter.status === 'fulfilled' && Array.isArray(scatter.value)
          ? scatter.value.filter((d) => d.total_volume > 0).slice(0, 2000)
          : []
      );

      // Greeks
      setGreeksData(
        greeks.status === 'fulfilled' && Array.isArray(greeks.value) ? greeks.value : []
      );

      // Volatility Surface
      setVolSurface(
        surface.status === 'fulfilled' && Array.isArray(surface.value) ? surface.value : []
      );

      // Pattern Analysis
      setPatternData(
        patterns.status === 'fulfilled' && patterns.value ? patterns.value : null
      );
    } catch {
      setOiData(generateMockOI());
      setVolSmileData(generateMockVolSmile());
      setHeatmapState(generateMockHeatmap());
      setCumulativeOI(generateMockCumulativeOI());
      setInsights(mockInsights);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Listen for header refresh button
  useEffect(() => {
    const handler = () => loadData();
    window.addEventListener('refresh-data', handler);
    return () => window.removeEventListener('refresh-data', handler);
  }, [loadData]);

  return (
    <div className="flex h-screen bg-[var(--bg-primary)]">
      {/* Sidebar */}
      <Sidebar filters={filters} onFilterChange={setFilters} />

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header />

        {loading && (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center space-y-3">
              <div className="w-8 h-8 border-2 border-[var(--blue)] border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-xs text-[var(--text-muted)]">Loading NIFTY analytics...</p>
            </div>
          </div>
        )}

        {!loading && (
        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* ROW 1: Market Pulse Metrics */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-1 h-5 rounded-full bg-[var(--blue)]" />
              <h2 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider">
                Market Pulse — NIFTY
              </h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <MetricCard
                label="Spot Price"
                value={marketData.spotPrice?.toLocaleString() ?? '—'}
                change={0}
                icon={<DollarSign size={18} />}
                color="--green"
                delay={0}
              />
              <MetricCard
                label="ATM Strike"
                value={marketData.atmStrike?.toLocaleString() ?? '—'}
                change={0}
                icon={<Target size={18} />}
                color="--blue"
                delay={0.1}
              />
              <MetricCard
                label="Put Call Ratio"
                value={marketData.pcr?.toFixed(3) ?? '—'}
                change={0}
                icon={<PieChart size={18} />}
                color="--cyan"
                delay={0.2}
              />
              <MetricCard
                label="Sentiment"
                value={marketData.sentiment}
                change={
                  marketData.sentiment === 'Bullish'
                    ? 1
                    : marketData.sentiment === 'Bearish'
                    ? -1
                    : 0
                }
                icon={<Activity size={18} />}
                color={
                  marketData.sentiment === 'Bullish'
                    ? '--green'
                    : marketData.sentiment === 'Bearish'
                    ? '--red'
                    : '--yellow'
                }
                delay={0.3}
              />
            </div>

            {/* Secondary metrics row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
              <MetricCard
                label="Total Open Interest"
                value={fmtNum(marketData.totalOI)}
                change={0}
                icon={<BarChart3 size={18} />}
                color="--blue"
                delay={0.4}
              />
              <MetricCard
                label="Total Volume"
                value={fmtNum(marketData.totalVolume)}
                change={0}
                icon={<TrendingUp size={18} />}
                color="--cyan"
                delay={0.5}
              />
              <MetricCard
                label="Anomalies Detected"
                value={marketData.anomaliesCount.toLocaleString()}
                change={0}
                icon={<AlertTriangle size={18} />}
                color="--yellow"
                delay={0.6}
              />
              <MetricCard
                label="Volume Spikes"
                value={marketData.volumeSpikes.toLocaleString()}
                change={0}
                icon={<Zap size={18} />}
                color="--red"
                delay={0.7}
              />
            </div>
          </section>

          {/* ROW 2: OI & Volume Distribution */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-1 h-5 rounded-full bg-[var(--cyan)]" />
              <h2 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider">
                Open Interest & Volume Distribution
              </h2>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <ChartCard
                title="Open Interest Distribution"
                subtitle="Where are traders positioned? Tall bars = heavy bets at that strike"
                delay={0.2}
              >
                <OIDistributionChart data={oiData} />
              </ChartCard>

              <ChartCard
                title="Volume Profile"
                subtitle="Today's trading activity — high volume = active interest at that strike"
                delay={0.25}
              >
                <VolumeProfileChart data={oiData} />
              </ChartCard>
            </div>
          </section>

          {/* ROW 3: Volatility Analysis */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-1 h-5 rounded-full bg-[var(--red)]" />
              <h2 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider">
                Volatility Analysis
              </h2>
              {patternData?.volatility_patterns?.skew_detected && (
                <span className="ml-2 text-[10px] px-2 py-0.5 rounded-full bg-[var(--yellow)] text-black font-bold uppercase">
                  Skew Detected
                </span>
              )}
              {patternData?.volatility_patterns?.smile_detected && (
                <span className="ml-1 text-[10px] px-2 py-0.5 rounded-full bg-[var(--cyan)] text-black font-bold uppercase">
                  Smile Detected
                </span>
              )}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <ChartCard
                title="Volatility Smile / Skew"
                subtitle="IV curve across strikes — U-shape = smile, tilt = skew (fear/greed)"
                delay={0.3}
              >
                <VolatilitySmileChart data={volSmileData} />
              </ChartCard>

              <ChartCard
                title="Volatility Surface"
                subtitle="IV landscape across strikes & expiries — bigger dots = more time to expiry"
                delay={0.35}
              >
                <VolatilitySurfaceChart data={volSurface} />
              </ChartCard>
            </div>

            {/* Pattern Analysis Summary */}
            {patternData && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-4">
                <div className="bg-[var(--bg-card)] border border-white/[0.06] rounded-lg p-3">
                  <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider mb-1">Skew Direction</p>
                  <p className="text-sm font-semibold text-[var(--text-primary)]">
                    {patternData.volatility_patterns?.skew_direction?.replace('_', ' ').toUpperCase() || 'Neutral'}
                  </p>
                  <p className="text-[10px] text-[var(--text-muted)] mt-1">Put skew = crash fear, Call skew = rally demand</p>
                </div>
                <div className="bg-[var(--bg-card)] border border-white/[0.06] rounded-lg p-3">
                  <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider mb-1">Smile Curvature</p>
                  <p className="text-sm font-semibold text-[var(--text-primary)]">
                    {patternData.volatility_patterns?.smile_curvature?.toFixed(4) ?? 'N/A'}
                  </p>
                  <p className="text-[10px] text-[var(--text-muted)] mt-1">Higher curvature = more uncertainty about direction</p>
                </div>
                <div className="bg-[var(--bg-card)] border border-white/[0.06] rounded-lg p-3">
                  <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider mb-1">Activity Clusters</p>
                  <p className="text-sm font-semibold text-[var(--text-primary)]">
                    {Object.keys(patternData.cluster_distribution || {}).length} groups
                  </p>
                  <p className="text-[10px] text-[var(--text-muted)] mt-1">KMeans groups strikes by trading intensity</p>
                </div>
                <div className="bg-[var(--bg-card)] border border-white/[0.06] rounded-lg p-3">
                  <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider mb-1">IV Spikes</p>
                  <p className="text-sm font-semibold text-[var(--text-primary)]">
                    {patternData.iv_spikes?.length || 0} detected
                  </p>
                </div>
              </div>
            )}
          </section>

          {/* ROW 4: Time Series Analytics */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-1 h-5 rounded-full bg-[var(--green)]" />
              <h2 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider">
                Time Series Analytics
              </h2>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <ChartCard
                title="PCR Timeseries & Spot Price"
                subtitle="PCR > 1 = bullish (more puts written), PCR < 1 = bearish. Yellow line = NIFTY spot"
                delay={0.35}
              >
                <PCRTimeseriesChart data={cumulativeOI} />
              </ChartCard>

              <ChartCard
                title="Cumulative Open Interest"
                subtitle="Total OI trend over time — rising OI = new positions, falling OI = exits"
                delay={0.4}
              >
                <CumulativeOIChart data={cumulativeOI} />
              </ChartCard>
            </div>
          </section>

          {/* ROW 5: Activity Heatmap */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-1 h-5 rounded-full bg-[var(--yellow)]" />
              <h2 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider">
                Activity Heatmap
              </h2>
            </div>
            <ChartCard
              title="Open Interest Heatmap"
              subtitle="OI intensity across strikes & timestamps"
              delay={0.4}
            >
              <Heatmap
                data={heatmapState.data}
                xLabels={heatmapState.times}
                yLabels={heatmapState.strikes}
              />
            </ChartCard>
          </section>

          {/* ROW 6: AI-Driven Pattern Detection */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-1 h-5 rounded-full bg-[var(--red)]" />
              <h2 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider">
                AI-Driven Pattern Detection
              </h2>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <ChartCard
                title="Anomaly Detection (Isolation Forest)"
                subtitle="Red dots = AI-flagged unusual trading patterns vs normal activity (blue)"
                delay={0.45}
              >
                <AnomalyScatterChart data={anomalyScatter} />
              </ChartCard>

              <ChartCard
                title="Options Greeks (Delta)"
                subtitle="Delta measures price sensitivity — Call delta (0→1), Put delta (0→-1)"
                delay={0.5}
              >
                <GreeksChart data={greeksData} />
              </ChartCard>
            </div>
          </section>

          {/* ROW 7: AI Insights Panel */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-1 h-5 rounded-full bg-[var(--yellow)]" />
              <h2 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider">
                AI Insights & Alerts
              </h2>
              <span className="ml-auto text-[10px] text-[var(--text-muted)]">
                {insights.length} insight{insights.length !== 1 ? 's' : ''} generated
              </span>
            </div>
            <div className="chart-container">
              <InsightsPanel
                insights={filters.showAnomalies ? insights : insights.filter((i) => i.type !== 'anomaly')}
              />
            </div>
          </section>

          {/* Footer */}
          <footer className="border-t border-white/[0.06] py-6 mt-4">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-7 h-7 rounded-md bg-gradient-to-br from-indigo-500 to-cyan-400 flex items-center justify-center">
                  <TrendingUp size={14} className="text-white" />
                </div>
                <span className="text-xs text-[var(--text-muted)]">
                  CodeForge Options Analytics · Built for CodeForge Hackathon 2026
                </span>
              </div>
              <div className="flex items-center gap-4">
                <button
                  onClick={() => navigate('/')}
                  className="text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors cursor-pointer"
                >
                  ← Back to Home
                </button>
                <p className="text-[11px] text-[var(--text-muted)]">
                  Made with FOSS ❤️ · React · TailwindCSS · Recharts · Python
                </p>
              </div>
            </div>
          </footer>
        </main>
        )}
      </div>
    </div>
  );
}
