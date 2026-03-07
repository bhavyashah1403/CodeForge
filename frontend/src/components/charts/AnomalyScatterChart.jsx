import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ZAxis,
} from 'recharts';

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  return (
    <div className="bg-[var(--bg-card)] border border-white/[0.1] rounded-lg p-3 shadow-xl">
      <p className="text-xs font-semibold text-[var(--text-primary)] mb-2">
        Strike: {Number(d?.strike).toLocaleString()}
      </p>
      <div className="space-y-1 text-xs">
        <div className="flex justify-between gap-4">
          <span className="text-[var(--text-secondary)]">Volume:</span>
          <span className="font-mono text-[var(--text-primary)]">
            {Number(d?.total_volume).toLocaleString()}
          </span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-[var(--text-secondary)]">OI:</span>
          <span className="font-mono text-[var(--text-primary)]">
            {Number(d?.total_oi).toLocaleString()}
          </span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-[var(--text-secondary)]">Anomaly:</span>
          <span
            className={`font-mono font-bold ${
              d?.is_anomaly ? 'text-[var(--red)]' : 'text-[var(--green)]'
            }`}
          >
            {d?.is_anomaly ? 'Yes' : 'No'}
          </span>
        </div>
        {d?.anomaly_score != null && (
          <div className="flex justify-between gap-4">
            <span className="text-[var(--text-secondary)]">Score:</span>
            <span className="font-mono text-[var(--text-primary)]">
              {Number(d?.anomaly_score).toFixed(4)}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default function AnomalyScatterChart({ data = [] }) {
  const normal = data.filter((d) => !d.is_anomaly);
  const anomalies = data.filter((d) => d.is_anomaly);

  return (
    <ResponsiveContainer width="100%" height={320}>
      <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
        <XAxis
          dataKey="strike"
          name="Strike"
          tick={{ fontSize: 10, fill: '#64748b' }}
          tickFormatter={(v) => (v / 1000).toFixed(1) + 'K'}
          axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
        />
        <YAxis
          dataKey="total_volume"
          name="Volume"
          tick={{ fontSize: 10, fill: '#64748b' }}
          tickFormatter={(v) =>
            v >= 1e6
              ? (v / 1e6).toFixed(1) + 'M'
              : v >= 1e3
              ? (v / 1e3).toFixed(0) + 'K'
              : v
          }
          axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
        />
        <ZAxis range={[20, 200]} />
        <Tooltip content={<CustomTooltip />} />
        <Legend
          wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
          iconType="circle"
          iconSize={8}
        />
        <Scatter
          name="Normal"
          data={normal}
          fill="#6366f1"
          fillOpacity={0.4}
          r={3}
        />
        <Scatter
          name="Anomaly"
          data={anomalies}
          fill="#ef4444"
          fillOpacity={0.8}
          r={5}
        />
      </ScatterChart>
    </ResponsiveContainer>
  );
}
