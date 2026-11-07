import React from "react";
import { Landmark, MapPin, Box, BookOpen, CheckCircle } from "lucide-react";

interface MetricsRowProps {
  totalSites: number;
  distinctStatesCount: number;
  coveredRegionsCount: number;
  total3dModels: number;
  totalSources: number;
}

export const MetricsRow: React.FC<MetricsRowProps> = ({
  totalSites,
  distinctStatesCount,
  coveredRegionsCount,
  total3dModels,
  totalSources,
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
              <span className="metric-badge verified">
                <CheckCircle className="w-3 h-3 inline mr-1 text-emerald-400" />
                Verified
              </span>
            </div>
            <span className="metric-label">Heritage Sites Documented</span>
            <span className="metric-subtext">Centrally Protected & ASI Baseline</span>
          </div>
        </div>
      </div>

      {/* Card 2: States / UTs Represented */}
      <div className="metric-card">
        <div className="metric-content">
          <div className="metric-icon-box gold-glow">
            <MapPin className="metric-icon text-amber-400" />
          </div>
          <div className="metric-details">
            <div className="metric-number-row">
              <span className="metric-value">{distinctStatesCount}</span>
              <span className="metric-badge neutral">
                {coveredRegionsCount} / 36 Ingestion Regions
              </span>
            </div>
            <span className="metric-label">States / UTs Represented</span>
            <span className="metric-subtext">Out of 36 Indian States & UTs</span>
          </div>
        </div>
      </div>

      {/* Card 3: Registered 3D Models */}
      <div className="metric-card">
        <div className="metric-content">
          <div className="metric-icon-box gold-glow">
            <Box className="metric-icon text-amber-400" />
          </div>
          <div className="metric-details">
            <div className="metric-number-row">
              <span className="metric-value">{total3dModels}</span>
              <span className="metric-badge neutral">Pipeline Ready</span>
            </div>
            <span className="metric-label">Registered 3D Models</span>
            <span className="metric-subtext">GLB • GLTF • OBJ • SPLAT Intake</span>
          </div>
        </div>
      </div>

      {/* Card 4: Archival Sources & Provenance */}
      <div className="metric-card">
        <div className="metric-content">
          <div className="metric-icon-box gold-glow">
            <BookOpen className="metric-icon text-amber-400" />
          </div>
          <div className="metric-details">
            <div className="metric-number-row">
              <span className="metric-value">{totalSources}</span>
              <span className="metric-badge verified">
                <CheckCircle className="w-3 h-3 inline mr-1 text-emerald-400" />
                100% Sourced
              </span>
            </div>
            <span className="metric-label">Archival Sources</span>
            <span className="metric-subtext">ASI & UNESCO Primary Citations</span>
          </div>
        </div>
      </div>
    </section>
  );
};
export default MetricsRow;
