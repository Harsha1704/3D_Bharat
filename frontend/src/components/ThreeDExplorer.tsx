import React from "react";
import { Box, ArrowRight, Play } from "lucide-react";
import type { HeritageSite } from "../api";

interface ThreeDExplorerProps {
  selectedSite: HeritageSite | null;
  onExplore3D: () => void;
}

export const ThreeDExplorer: React.FC<ThreeDExplorerProps> = ({
  selectedSite,
  onExplore3D,
}) => {
  const monumentTitle = selectedSite
    ? selectedSite.name
    : "Konark Sun Temple";

  return (
    <div className="bottom-panel-card three-d-panel">
      {/* Panel Header */}
      <div className="panel-header">
        <div className="panel-title-group">
          <Box className="panel-icon text-amber-400" />
          <h3 className="panel-title">3D Exploration</h3>
        </div>
        <button className="panel-action-link" onClick={onExplore3D}>
          <span>View All</span>
          <ArrowRight className="w-4 h-4 ml-1 inline" />
        </button>
      </div>

      {/* 3D Showcase Card */}
      <div className="three-d-hero-card" onClick={onExplore3D}>
        <img
          src="https://images.unsplash.com/photo-1600100397608-f010f44390b2?auto=format&fit=crop&w=800&q=80"
          alt={monumentTitle}
          className="three-d-cover-img"
        />

        {/* 360 Degree Floating Badge */}
        <div className="three-sixty-badge">
          <svg className="three-sixty-icon" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="9" stroke="#FFC857" strokeWidth="1.5" strokeDasharray="3 3" />
            <path d="M12 7 L15 10 L12 13" fill="none" stroke="#FFC857" strokeWidth="1.5" />
          </svg>
          <span>360°</span>
        </div>

        {/* Central Play / Orbit Button Overlay */}
        <div className="three-d-play-overlay">
          <button className="play-pulse-btn" aria-label="Start 3D Tour">
            <Play className="w-6 h-6 text-amber-900 fill-amber-900 ml-0.5" />
          </button>
        </div>

        {/* Bottom Banner Info */}
        <div className="three-d-card-caption">
          <div className="caption-left">
            <div className="caption-title-row">
              <Play className="w-3.5 h-3.5 text-amber-400 fill-amber-400 mr-1.5" />
              <span className="caption-headline">Explore in 3D</span>
            </div>
            <p className="caption-subline">
              Virtual Tour of {monumentTitle}
            </p>
          </div>
          <div className="format-tags">
            <span className="format-pill">GLB</span>
            <span className="format-pill">GLTF</span>
            <span className="format-pill">OBJ</span>
            <span className="format-pill">SPLAT</span>
          </div>
        </div>
      </div>
    </div>
  );
};
export default ThreeDExplorer;
