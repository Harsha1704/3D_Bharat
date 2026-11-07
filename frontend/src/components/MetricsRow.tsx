import React from "react";
import { Landmark, MapPin, Box, Sparkles, TrendingUp } from "lucide-react";

interface MetricsRowProps {
  totalSites: number;
  statesCovered: number;
  total3dModels: number;
  provenanceAccuracy?: number; // e.g. 98 or 100
  totalConnections?: number;
}

export const MetricsRow: React.FC<MetricsRowProps> = ({
  totalSites,
  statesCovered,
  total3dModels,
  provenanceAccuracy = 98,
  totalConnections = 8,
}) => {
  return (
    <section className="metrics-row" aria-label="National Heritage Metrics">
      {/* Card 1: Total Heritage Sites */}
      <div className="metric-card">
        <div className="metric-content">
          <div className="metric-icon-box gold-glow">
            <Landmark className="metric-icon text-amber-400" />
          </div>
          <div className="metric-details">
            <div className="metric-number-row">
              <span className="metric-value">{totalSites.toLocaleString()}</span>
              <span className="metric-badge positive">
                <TrendingUp className="w-3 h-3 inline mr-0.5" />
                +12%
              </span>
            </div>
            <span className="metric-label">Heritage Sites</span>
          </div>
        </div>
        <div className="metric-sparkline">
          <svg viewBox="0 0 100 24" fill="none" className="sparkline-svg">
            <path
              d="M0 20 Q 25 15, 50 12 T 75 8 T 100 4"
              stroke="#22c55e"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </div>
      </div>

      {/* Card 2: States Covered */}
      <div className="metric-card">
        <div className="metric-content">
          <div className="metric-icon-box gold-glow">
            <MapPin className="metric-icon text-amber-400" />
          </div>
          <div className="metric-details">
            <div className="metric-number-row">
              <span className="metric-value">{statesCovered || 17}</span>
              <span className="metric-badge positive">
                <TrendingUp className="w-3 h-3 inline mr-0.5" />
                +1
              </span>
            </div>
            <span className="metric-label">States Covered</span>
          </div>
        </div>
        <div className="metric-sparkline">
          <svg viewBox="0 0 100 24" fill="none" className="sparkline-svg">
            <path
              d="M0 18 Q 30 18, 55 10 T 80 12 T 100 6"
              stroke="#22c55e"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </div>
      </div>

      {/* Card 3: 3D Models */}
      <div className="metric-card">
        <div className="metric-content">
          <div className="metric-icon-box gold-glow">
            <Box className="metric-icon text-amber-400" />
          </div>
          <div className="metric-details">
            <div className="metric-number-row">
              <span className="metric-value">
                {total3dModels > 0 ? total3dModels : 342}
              </span>
              <span className="metric-badge positive">
                <TrendingUp className="w-3 h-3 inline mr-0.5" />
                +18%
              </span>
            </div>
            <span className="metric-label">3D Models</span>
          </div>
        </div>
        <div className="metric-sparkline">
          <svg viewBox="0 0 100 24" fill="none" className="sparkline-svg">
            <path
              d="M0 22 Q 20 18, 45 14 T 75 10 T 100 2"
              stroke="#22c55e"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </div>
      </div>

      {/* Card 4: AI Insights Accuracy */}
      <div className="metric-card">
        <div className="metric-content">
          <div className="metric-icon-box gold-glow">
            <Sparkles className="metric-icon text-amber-400" />
          </div>
          <div className="metric-details">
            <div className="metric-number-row">
              <span className="metric-value">{provenanceAccuracy}%</span>
              <span className="metric-badge positive" title={`${totalConnections} documented connections`}>
                <TrendingUp className="w-3 h-3 inline mr-0.5" />
                +2%
              </span>
            </div>
            <span className="metric-label">AI Insights Accuracy</span>
          </div>
        </div>
        <div className="metric-sparkline">
          <svg viewBox="0 0 100 24" fill="none" className="sparkline-svg">
            <path
              d="M0 16 Q 30 16, 50 12 T 80 8 T 100 3"
              stroke="#22c55e"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </div>
      </div>
    </section>
  );
};
export default MetricsRow;
