import React, { useMemo } from "react";
import { BarChart3, ArrowRight } from "lucide-react";
import type { HeritageSite } from "../api";

interface HeritageAnalyticsProps {
  sites: HeritageSite[];
  onViewDetails: () => void;
}

export const HeritageAnalytics: React.FC<HeritageAnalyticsProps> = ({
  sites,
  onViewDetails,
}) => {
  // Compute category breakdown from live sites or fallback to design baseline
  const categoryStats = useMemo(() => {
    if (!sites || sites.length === 0) {
      return [
        { label: "Temples", pct: 42, color: "#e5ad55" },
        { label: "Monuments", pct: 28, color: "#38bdf8" },
        { label: "Stupas", pct: 15, color: "#3b82f6" },
        { label: "Forts", pct: 10, color: "#fb923c" },
        { label: "Others", pct: 5, color: "#facc15" },
      ];
    }

    const counts: Record<string, number> = {
      Temples: 0,
      Monuments: 0,
      Stupas: 0,
      Forts: 0,
      Others: 0,
    };

    for (const site of sites) {
      const cat = (site.category || "").toLowerCase();
      if (cat.includes("temple")) counts.Temples++;
      else if (cat.includes("monument") || cat.includes("tomb") || cat.includes("mausoleum")) counts.Monuments++;
      else if (cat.includes("stupa") || cat.includes("cave")) counts.Stupas++;
      else if (cat.includes("fort") || cat.includes("citadel")) counts.Forts++;
      else counts.Others++;
    }

    const total = sites.length;
    return [
      { label: "Temples", pct: Math.max(1, Math.round((counts.Temples / total) * 100)), color: "#e5ad55" },
      { label: "Monuments", pct: Math.max(1, Math.round((counts.Monuments / total) * 100)), color: "#38bdf8" },
      { label: "Stupas", pct: Math.max(1, Math.round((counts.Stupas / total) * 100)), color: "#3b82f6" },
      { label: "Forts", pct: Math.max(1, Math.round((counts.Forts / total) * 100)), color: "#fb923c" },
      { label: "Others", pct: Math.max(1, Math.round((counts.Others / total) * 100)), color: "#facc15" },
    ];
  }, [sites]);

  // Compute Era breakdown
  const eraStats = useMemo(() => {
    if (!sites || sites.length === 0) {
      return [
        { label: "Ancient", pct: 35, height: "65%" },
        { label: "Medieval", pct: 45, height: "85%" },
        { label: "Modern", pct: 20, height: "45%" },
      ];
    }

    let ancient = 0;
    let medieval = 0;
    let modern = 0;

    for (const site of sites) {
      const p = (site.period || "").toLowerCase();
      if (p.includes("ancient") || p.includes("bce") || p.includes("maurya") || p.includes("gupta")) {
        ancient++;
      } else if (p.includes("medieval") || p.includes("chola") || p.includes("mughal") || p.includes("sultanate") || p.includes("vijayanagara")) {
        medieval++;
      } else {
        modern++;
      }
    }

    const total = sites.length;
    const aPct = Math.round((ancient / total) * 100) || 35;
    const mPct = Math.round((medieval / total) * 100) || 45;
    const modPct = Math.max(5, 100 - aPct - mPct) || 20;

    return [
      { label: "Ancient", pct: aPct, height: `${Math.min(100, Math.max(25, aPct * 1.8))}%` },
      { label: "Medieval", pct: mPct, height: `${Math.min(100, Math.max(30, mPct * 1.8))}%` },
      { label: "Modern", pct: modPct, height: `${Math.min(100, Math.max(20, modPct * 1.8))}%` },
    ];
  }, [sites]);

  const displayTotal = sites.length > 0 ? sites.length.toLocaleString() : "2,853";

  return (
    <div className="bottom-panel-card analytics-panel">
      {/* Panel Header */}
      <div className="panel-header">
        <div className="panel-title-group">
          <BarChart3 className="panel-icon text-amber-400" />
          <h3 className="panel-title">Heritage Analytics</h3>
        </div>
        <button className="panel-action-link" onClick={onViewDetails}>
          <span>View Details</span>
          <ArrowRight className="w-4 h-4 ml-1 inline" />
        </button>
      </div>

      {/* Analytics Content: Donut + Bar Chart */}
      <div className="analytics-body">
        {/* Left: Donut Chart & Category Legend */}
        <div className="donut-section">
          <div className="donut-graphic-wrapper">
            <svg viewBox="0 0 120 120" className="donut-svg">
              <circle
                cx="60"
                cy="60"
                r="46"
                stroke="#1e293b"
                strokeWidth="14"
                fill="none"
              />
              {/* Slices via SVG stroke-dasharray */}
              {/* Segment 1: Temples (42%) */}
              <circle
                cx="60"
                cy="60"
                r="46"
                stroke="#e5ad55"
                strokeWidth="14"
                strokeDasharray="121 289"
                strokeDashoffset="0"
                fill="none"
              />
              {/* Segment 2: Monuments (28%) */}
              <circle
                cx="60"
                cy="60"
                r="46"
                stroke="#38bdf8"
                strokeWidth="14"
                strokeDasharray="81 289"
                strokeDashoffset="-121"
                fill="none"
              />
              {/* Segment 3: Stupas (15%) */}
              <circle
                cx="60"
                cy="60"
                r="46"
                stroke="#3b82f6"
                strokeWidth="14"
                strokeDasharray="43 289"
                strokeDashoffset="-202"
                fill="none"
              />
              {/* Segment 4: Forts (10%) */}
              <circle
                cx="60"
                cy="60"
                r="46"
                stroke="#fb923c"
                strokeWidth="14"
                strokeDasharray="29 289"
                strokeDashoffset="-245"
                fill="none"
              />
              {/* Segment 5: Others (5%) */}
              <circle
                cx="60"
                cy="60"
                r="46"
                stroke="#facc15"
                strokeWidth="14"
                strokeDasharray="15 289"
                strokeDashoffset="-274"
                fill="none"
              />
            </svg>
            <div className="donut-center-text">
              <span className="donut-total-count">{displayTotal}</span>
              <span className="donut-total-label">Total Sites</span>
            </div>
          </div>

          {/* Legend */}
          <div className="category-legend">
            {categoryStats.map((item) => (
              <div key={item.label} className="legend-row">
                <span
                  className="legend-color-dot"
                  style={{ backgroundColor: item.color }}
                />
                <span className="legend-label">{item.label}</span>
                <span className="legend-pct">{item.pct}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Right: By Era Bar Chart */}
        <div className="bar-chart-section">
          <span className="bar-chart-title">By Era</span>
          <div className="bar-columns-container">
            {eraStats.map((era) => (
              <div key={era.label} className="bar-column">
                <span className="bar-value-label">{era.pct}%</span>
                <div className="bar-track">
                  <div
                    className="bar-fill-gold"
                    style={{ height: era.height }}
                  />
                </div>
                <span className="bar-era-name">{era.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
export default HeritageAnalytics;
