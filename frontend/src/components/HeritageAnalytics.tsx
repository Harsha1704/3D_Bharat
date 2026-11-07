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
  // Compute category breakdown from actual loaded database records
  const categoryStats = useMemo(() => {
    if (!sites || sites.length === 0) {
      return [];
    }

    const counts: Record<string, number> = {
      "Temples & Shrines": 0,
      "Forts & Fortresses": 0,
      "Stupas & Archaeology": 0,
      "Stepwells": 0,
      "Rock-cut Caves": 0,
      "Mausoleums & Tombs": 0,
    };

    let otherCount = 0;

    for (const site of sites) {
      const cat = (site.category || "").toLowerCase();
      if (cat.includes("temple") || cat.includes("shrine")) {
        counts["Temples & Shrines"]++;
      } else if (cat.includes("fort") || cat.includes("citadel") || cat.includes("fortress")) {
        counts["Forts & Fortresses"]++;
      } else if (cat.includes("stupa") || cat.includes("archaeological")) {
        counts["Stupas & Archaeology"]++;
      } else if (cat.includes("stepwell")) {
        counts["Stepwells"]++;
      } else if (cat.includes("cave") || cat.includes("rock-cut")) {
        counts["Rock-cut Caves"]++;
      } else if (cat.includes("mausoleum") || cat.includes("tomb")) {
        counts["Mausoleums & Tombs"]++;
      } else {
        otherCount++;
      }
    }

    const total = sites.length;
    const colors = ["#e5ad55", "#38bdf8", "#3b82f6", "#fb923c", "#10b981", "#a855f7", "#94a3b8"];

    const items = Object.entries(counts)
      .filter(([_, count]) => count > 0)
      .map(([label, count], idx) => ({
        label,
        count,
        pct: Math.round((count / total) * 100),
        color: colors[idx % colors.length],
      }));

    if (otherCount > 0) {
      items.push({
        label: "Others / Regional",
        count: otherCount,
        pct: Math.round((otherCount / total) * 100),
        color: colors[items.length % colors.length],
      });
    }

    return items;
  }, [sites]);

  // Compute Era breakdown from actual recorded periods
  const eraStats = useMemo(() => {
    if (!sites || sites.length === 0) {
      return [];
    }

    let ancient = 0;
    let medieval = 0;
    let modern = 0;

    for (const site of sites) {
      const p = (site.period || "").toLowerCase();
      if (
        p.includes("bce") ||
        p.includes("3000 bce") ||
        p.includes("maurya") ||
        p.includes("gupta") ||
        p.includes("3rd century bce") ||
        p.includes("2nd century bce") ||
        p.includes("5th century bce") ||
        p.includes("6th century bce")
      ) {
        ancient++;
      } else if (
        p.includes("17th century") ||
        p.includes("18th century") ||
        p.includes("19th century") ||
        p.includes("1631") ||
        p.includes("mughal")
      ) {
        modern++;
      } else {
        // 7th to 16th Century CE / Chola / Vijayanagara / Chandela / Kakatiya / Hoysala
        medieval++;
      }
    }

    const total = sites.length;
    const aPct = Math.round((ancient / total) * 100);
    const mPct = Math.round((medieval / total) * 100);
    const modPct = 100 - aPct - mPct;

    return [
      { label: "Ancient", count: ancient, pct: aPct, height: `${Math.min(100, Math.max(20, aPct * 1.5))}%` },
      { label: "Medieval", count: medieval, pct: mPct, height: `${Math.min(100, Math.max(20, mPct * 1.2))}%` },
      { label: "Modern", count: modern, pct: modPct, height: `${Math.min(100, Math.max(15, modPct * 2.5))}%` },
    ];
  }, [sites]);

  const totalSitesCount = sites.length;
  const CIRCUMFERENCE = 289; // 2 * PI * 46

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
              {/* Dynamic Slices based on actual category percentages */}
              {(() => {
                let accumulatedOffset = 0;
                return categoryStats.map((item) => {
                  const strokeLength = (item.pct / 100) * CIRCUMFERENCE;
                  const currentOffset = accumulatedOffset;
                  accumulatedOffset += strokeLength;

                  return (
                    <circle
                      key={item.label}
                      cx="60"
                      cy="60"
                      r="46"
                      stroke={item.color}
                      strokeWidth="14"
                      strokeDasharray={`${strokeLength} ${CIRCUMFERENCE}`}
                      strokeDashoffset={-currentOffset}
                      fill="none"
                    />
                  );
                });
              })()}
            </svg>
            <div className="donut-center-text">
              <span className="donut-total-count">{totalSitesCount}</span>
              <span className="donut-total-label">Total Sites</span>
            </div>
          </div>

          {/* Legend */}
          <div className="category-legend">
            {categoryStats.slice(0, 4).map((item) => (
              <div key={item.label} className="legend-row">
                <span
                  className="legend-color-dot"
                  style={{ backgroundColor: item.color }}
                />
                <span className="legend-label">{item.label}</span>
                <span className="legend-pct">
                  {item.pct}% ({item.count})
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Right: By Era Bar Chart */}
        <div className="bar-chart-section">
          <span className="bar-chart-title">By Era (CE/BCE)</span>
          <div className="bar-columns-container">
            {eraStats.map((era) => (
              <div key={era.label} className="bar-column" title={`${era.count} sites recorded`}>
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
