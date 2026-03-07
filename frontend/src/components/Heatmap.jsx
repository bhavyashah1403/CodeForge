import { useMemo, useState } from 'react';
import { motion } from 'framer-motion';

/**
 * Heatmap – Volume heatmap grid (Time x Strike, colored by volume).
 *
 * Props:
 *  - data: [{ time, strike, volume }, ...]
 *  - xLabels: array of time strings
 *  - yLabels: array of strike numbers
 */

function getColor(value, min, max) {
  if (value === 0) return 'rgba(15, 23, 42, 0.8)';
  const ratio = Math.min((value - min) / (max - min || 1), 1);

  if (ratio < 0.25) {
    const t = ratio / 0.25;
    return `rgba(30, ${Math.round(58 + t * 60)}, ${Math.round(138 + t * 20)}, 0.9)`;
  }
  if (ratio < 0.5) {
    const t = (ratio - 0.25) / 0.25;
    return `rgba(${Math.round(34 + t * 160)}, ${Math.round(197 - t * 50)}, ${Math.round(94 - t * 60)}, 0.9)`;
  }
  if (ratio < 0.75) {
    const t = (ratio - 0.5) / 0.25;
    return `rgba(${Math.round(234 - t * 40)}, ${Math.round(179 - t * 80)}, ${Math.round(8 + t * 10)}, 0.9)`;
  }
  const t = (ratio - 0.75) / 0.25;
  return `rgba(${Math.round(239 - t * 20)}, ${Math.round(68 - t * 30)}, ${Math.round(68 - t * 30)}, 0.95)`;
}

export default function Heatmap({ data = [], xLabels = [], yLabels = [] }) {
  const [hoveredCell, setHoveredCell] = useState(null);

  const { grid, min, max } = useMemo(() => {
    if (!data.length) {
      return { grid: {}, min: 0, max: 1 };
    }
    const g = {};
    let mn = Infinity;
    let mx = -Infinity;
    data.forEach((d) => {
      const key = `${d.time}__${d.strike}`;
      g[key] = d.volume;
      if (d.volume > 0) {
        mn = Math.min(mn, d.volume);
        mx = Math.max(mx, d.volume);
      }
    });
    if (mn === Infinity) mn = 0;
    return { grid: g, min: mn, max: mx };
  }, [data]);

  const cellSize = Math.max(24, Math.min(40, 600 / Math.max(xLabels.length, 1)));

  return (
    <div className="relative overflow-auto max-h-[380px]">
      {/* Tooltip */}
      {hoveredCell && (
        <div
          className="fixed z-50 pointer-events-none bg-[var(--bg-card)] border border-white/[0.1] rounded-lg p-2.5 shadow-xl text-xs"
          style={{ left: hoveredCell.x + 12, top: hoveredCell.y - 40 }}
        >
          <p className="text-[var(--text-muted)]">
            {hoveredCell.time} · Strike {Number(hoveredCell.strike).toLocaleString()}
          </p>
          <p className="text-[var(--text-primary)] font-mono font-semibold mt-0.5">
            Vol: {Number(hoveredCell.volume).toLocaleString()}
          </p>
        </div>
      )}

      <div className="inline-block">
        {/* X-axis labels */}
        <div className="flex" style={{ paddingLeft: 60 }}>
          {xLabels.map((t, i) => (
            <div
              key={i}
              className="text-[9px] text-[var(--text-muted)] text-center shrink-0"
              style={{ width: cellSize }}
            >
              {i % Math.ceil(xLabels.length / 10) === 0 ? t : ''}
            </div>
          ))}
        </div>

        {/* Grid rows */}
        {yLabels.map((strike, yi) => (
          <div key={yi} className="flex items-center">
            {/* Y-axis label */}
            <div className="w-[60px] text-[10px] text-[var(--text-muted)] text-right pr-2 font-mono shrink-0">
              {(strike / 1000).toFixed(1)}K
            </div>

            {/* Cells */}
            {xLabels.map((time, xi) => {
              const key = `${time}__${strike}`;
              const volume = grid[key] || 0;
              const bg = getColor(volume, min, max);

              return (
                <div
                  key={xi}
                  className="shrink-0 border border-white/[0.02] transition-all duration-150 cursor-crosshair hover:border-white/20 hover:scale-110 hover:z-10"
                  style={{
                    width: cellSize,
                    height: cellSize,
                    background: bg,
                  }}
                  onMouseEnter={(e) =>
                    setHoveredCell({
                      x: e.clientX,
                      y: e.clientY,
                      time,
                      strike,
                      volume,
                    })
                  }
                  onMouseMove={(e) =>
                    setHoveredCell((prev) =>
                      prev ? { ...prev, x: e.clientX, y: e.clientY } : null
                    )
                  }
                  onMouseLeave={() => setHoveredCell(null)}
                />
              );
            })}
          </div>
        ))}
      </div>

      {/* Color legend */}
      <div className="flex items-center gap-2 mt-3 pl-[60px]">
        <span className="text-[10px] text-[var(--text-muted)]">Low</span>
        <div className="flex h-3 rounded-sm overflow-hidden">
          {[0, 0.25, 0.5, 0.75, 1].map((r, i) => (
            <div
              key={i}
              className="w-8 h-full"
              style={{ background: getColor(min + r * (max - min), min, max) }}
            />
          ))}
        </div>
        <span className="text-[10px] text-[var(--text-muted)]">High</span>
      </div>
    </div>
  );
}
