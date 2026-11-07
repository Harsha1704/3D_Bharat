import React from "react";
import { Box, ArrowRight, UploadCloud, ShieldCheck } from "lucide-react";
import type { Heritage3DAsset } from "../api";

interface ThreeDExplorerProps {
  assets3D?: Heritage3DAsset[];
  onExplore3D: () => void;
}

export const ThreeDExplorer: React.FC<ThreeDExplorerProps> = ({
  assets3D = [],
  onExplore3D,
}) => {
  const hasModels = assets3D.length > 0;

  return (
    <div className="bottom-panel-card three-d-panel">
      {/* Panel Header */}
      <div className="panel-header">
        <div className="panel-title-group">
          <Box className="panel-icon text-amber-400" />
          <h3 className="panel-title">3D Digital Preservation</h3>
        </div>
        <button className="panel-action-link" onClick={onExplore3D}>
          <span>{hasModels ? "View Assets" : "Pipeline Info"}</span>
          <ArrowRight className="w-4 h-4 ml-1 inline" />
        </button>
      </div>

      {/* 3D Showcase or Honest Pipeline Empty State */}
      {hasModels ? (
        <div className="three-d-hero-card" onClick={onExplore3D}>
          <div className="three-d-card-caption">
            <div className="caption-left">
              <span className="caption-headline">{assets3D[0].title}</span>
              <p className="caption-subline">
                Format: {assets3D[0].file_format.toUpperCase()} • {assets3D[0].vertex_count || 0} Vertices
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="three-d-empty-state">
          <div className="empty-state-icon-ring">
            <Box className="w-8 h-8 text-amber-400" />
          </div>
          <h4 className="empty-state-title">No 3D Models Registered Yet</h4>
          <p className="empty-state-desc">
            The national 3D photogrammetry intake is active and ready to register
            verified scans (GLB, GLTF, OBJ with MTL companions, and SPLAT)
            under the Phase 4 preservation standard.
          </p>
          <div className="empty-state-actions">
            <button className="btn-empty-action" onClick={onExplore3D}>
              <UploadCloud className="w-3.5 h-3.5 mr-1.5 inline" />
              <span>Register 3D Scan</span>
            </button>
            <span className="pipeline-status-badge">
              <ShieldCheck className="w-3 h-3 mr-1 inline text-emerald-400" />
              Ingestion Ready (0 / 0 Assets)
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
export default ThreeDExplorer;
