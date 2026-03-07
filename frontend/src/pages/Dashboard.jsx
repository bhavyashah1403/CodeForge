import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  DollarSign,
  Target,
  PieChart,
  Activity,
} from 'lucide-react';

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

// API
import {
  fetchMarketSummary,
  fetchOpenInterest,
  fetchVolatilitySmile,
  fetchVolumeHeatmap,
  fetchAIInsights,
  fetchCumulativeOI,
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
      iv: 12 + dist * dist * 1.8 + (Math.random() - 0.5) * 1.5,
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
      'Strike 25,800 saw a 400% spike in Put Volume at 11:30. This is unusual and may indicate institutional hedging activity.',
    timestamp: '11:30 AM · 07 Mar 2026',
    severity: 'high',
  },
  {
    id: 2,
    type: 'bullish',
    title: 'Sentiment Shift',
    description:
      'PCR moved from 0.8 to 1.2 in the last hour, suggesting a shift toward bullish sentiment as puts are being written aggressively.',
    timestamp: '11:15 AM · 07 Mar 2026',
    severity: 'medium',
  },
  {
    id: 3,
    type: 'volatility',
    title: 'Volatility Alert',
    description:
      'Volatility skew is increasing — far OTM puts are being bid up, suggesting crash protection demand is rising.',
    timestamp: '10:45 AM · 07 Mar 2026',
    severity: 'high',
  },
  {
    id: 4,
    type: 'spike',
    title: 'Volume Spike',
    description:
      'Call OI at strike 25,000 increased by 1.2M in 30 minutes. Highest activity today.',
    timestamp: '10:30 AM · 07 Mar 2026',
    severity: 'medium',
  },
  {
    id: 5,
    type: 'bearish',
    title: 'Resistance Build-up',
    description:
      'Heavy Call writing observed at 25,500 strike with 2.5M OI. This may act as key resistance.',
    timestamp: '10:00 AM · 07 Mar 2026',
    severity: 'low',
  },
  {
    id: 6,
    type: 'info',
    title: 'Max Pain Analysis',
    description:
      'Max Pain is at 24,800 for current expiry. Market is currently trading 200 points above Max Pain.',
    timestamp: '09:30 AM · 07 Mar 2026',
    severity: 'low',
  },
];

// ── Dashboard Page ───────────────────────────────────────────────

export default function Dashboard() {
  const [filters, setFilters] = useState({
    asset: 'NIFTY',
    expiry: '2026-02-17',
    strikeRange: 25000,
    timeRange: 6,
    showAnomalies: true,
  });

  const [marketData, setMarketData] = useState({
    spotPrice: 24587.35,
    atmStrike: 24600,
    pcr: 1.14,
    avgIV: 14.82,
    spotChange: 0.73,
    pcrChange: -2.14,
    ivChange: 1.56,
  });

  const [oiData, setOiData] = useState([]);
  const [volSmileData, setVolSmileData] = useState([]);
  const [heatmapState, setHeatmapState] = useState({ data: [], times: [], strikes: [] });
  const [cumulativeOI, setCumulativeOI] = useState([]);
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      // Try fetching from backend — fall back to mock data
      const [summary, oi, volSmile, heatmap, aiInsights, cumOI] =
        await Promise.allSettled([
          fetchMarketSummary(filters),
          fetchOpenInterest(filters),
          fetchVolatilitySmile(filters),
          fetchVolumeHeatmap(filters),
          fetchAIInsights(filters),
          fetchCumulativeOI(filters),
        ]);

      setMarketData(
        summary.status === 'fulfilled' && summary.value
          ? summary.value
          : {
              spotPrice: 24587.35,
              atmStrike: 24600,
              pcr: 1.14,
              avgIV: 14.82,
              spotChange: 0.73,
              pcrChange: -2.14,
              ivChange: 1.56,
            }
      );

      setOiData(
        oi.status === 'fulfilled' && Array.isArray(oi.value)
          ? oi.value
          : generateMockOI()
      );

      setVolSmileData(
        volSmile.status === 'fulfilled' && Array.isArray(volSmile.value)
          ? volSmile.value
          : generateMockVolSmile()
      );

      if (heatmap.status === 'fulfilled' && heatmap.value?.data) {
        setHeatmapState(heatmap.value);
      } else {
        setHeatmapState(generateMockHeatmap());
      }

      setCumulativeOI(
        cumOI.status === 'fulfilled' && Array.isArray(cumOI.value)
          ? cumOI.value
          : generateMockCumulativeOI()
      );

      setInsights(
        aiInsights.status === 'fulfilled' && Array.isArray(aiInsights.value)
          ? aiInsights.value
          : mockInsights
      );
    } catch {
      // Full fallback
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

        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* ROW 1: Market Pulse Metrics */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-1 h-5 rounded-full bg-[var(--blue)]" />
              <h2 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider">
                Market Pulse
              </h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <MetricCard
                label="Spot Price"
                value={marketData.spotPrice}
                change={marketData.spotChange}
                icon={<DollarSign size={18} />}
                color="--green"
                delay={0}
              />
              <MetricCard
                label="ATM Strike"
                value={marketData.atmStrike}
                change={0.0}
                icon={<Target size={18} />}
                color="--blue"
                delay={0.1}
              />
              <MetricCard
                label="Put Call Ratio"
                value={marketData.pcr}
                change={marketData.pcrChange}
                icon={<PieChart size={18} />}
                color="--cyan"
                delay={0.2}
              />
              <MetricCard
                label="Avg Implied Volatility"
                value={`${marketData.avgIV}%`}
                change={marketData.ivChange}
                icon={<Activity size={18} />}
                color="--yellow"
                delay={0.3}
              />
            </div>
          </section>

          {/* ROW 2: Structural Market Insights */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-1 h-5 rounded-full bg-[var(--cyan)]" />
              <h2 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider">
                Structural Market Insights
              </h2>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <ChartCard
                title="Open Interest Distribution"
                subtitle="Call vs Put OI across strikes"
                delay={0.2}
              >
                <OIDistributionChart data={oiData} />
              </ChartCard>

              <ChartCard
                title="Volatility Smile"
                subtitle="Strike vs Implied Volatility"
                delay={0.3}
              >
                <VolatilitySmileChart data={volSmileData} />
              </ChartCard>
            </div>
          </section>

          {/* ROW 3: Time Series Analytics */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-1 h-5 rounded-full bg-[var(--green)]" />
              <h2 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider">
                Time Series Analytics
              </h2>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <ChartCard
                title="Volume Heatmap"
                subtitle="Trading volume by time & strike"
                delay={0.3}
              >
                <Heatmap
                  data={heatmapState.data}
                  xLabels={heatmapState.times}
                  yLabels={heatmapState.strikes}
                />
              </ChartCard>

              <ChartCard
                title="Cumulative Open Interest Change"
                subtitle="Call & Put OI trend over time"
                delay={0.4}
              >
                <CumulativeOIChart data={cumulativeOI} />
              </ChartCard>
            </div>
          </section>

          {/* ROW 4: AI Insights Panel */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-1 h-5 rounded-full bg-[var(--yellow)]" />
              <h2 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider">
                AI Insights & Alerts
              </h2>
            </div>
            <div className="chart-container">
              <InsightsPanel
                insights={filters.showAnomalies ? insights : insights.filter((i) => i.type !== 'anomaly')}
              />
            </div>
          </section>

          {/* Footer */}
          <footer className="text-center py-4 border-t border-white/[0.04]">
            <p className="text-[11px] text-[var(--text-muted)]">
              CodeForge Options Analytics · Built with React · Recharts · TailwindCSS — FOSS ❤️
            </p>
          </footer>
        </main>
      </div>
    </div>
  );
}
