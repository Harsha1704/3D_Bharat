import React from "react";
import {
  Box,
  ArrowRight,
  UploadCloud,
  ShieldCheck,
  Lock,
  Scan,
} from "lucide-react";
import type { Heritage3DAsset } from "../api";

interface ThreeDExplorerProps {
  assets3D?: Heritage3DAsset[];
  onExplore3D?: () => void;
  isFullPage?: boolean;
}

export const ThreeDExplorer: React.FC<ThreeDExplorerProps> = ({
  assets3D = [],
  onExplore3D,
  isFullPage = false,
}) => {
  const hasModels = assets3D.length > 0;

  if (isFullPage) {
    return (
      <div className="preservation-workspace-container">
        {/* Workspace Header */}
        <div className="preservation-header-bar">
          <div>
            <div className="flex items-center gap-2">
              <Box className="w-5 h-5 text-amber-400" />
              <h2 className="text-xl font-bold text-white tracking-wide">
                3D Digital Preservation & Photogrammetry Archives
              </h2>
            </div>
            <p className="text-xs text-gray-400 mt-1">
              National archival repository for millimeter-accurate laser scans, photogrammetry models, and 3D Gaussian Splats.
            </p>
          </div>

          <div className="preservation-badge-pill">
            <span className="live-pulse-dot" />
            <span>Phase 4 Preservation Standard • Zero Models Registered</span>
          </div>
        </div>

        {/* Empty State / Intake Architecture */}
        <div className="preservation-showcase-panel">
          <div className="preservation-empty-card">
            <div className="empty-icon-halo">
              <Scan className="w-10 h-10 text-amber-400" />
            </div>

            <h3 className="text-lg font-bold text-white mt-3">
              National 3D Photogrammetry Archive Active
            </h3>
            <p className="text-sm text-gray-400 max-w-xl text-center mt-2 leading-relaxed">
              No 3D models have been registered yet in the primary database. The national preservation pipeline is initialized and accepts verified archaeological captures with cryptographic SHA-256 integrity verification.
            </p>

            <div className="supported-formats-row mt-6">
              <div className="format-badge">
                <span className="format-ext">.GLB</span>
                <span className="format-desc">Binary GLTF with embedded PBR textures</span>
              </div>
              <div className="format-badge">
                <span className="format-ext">.GLTF</span>
                <span className="format-desc">JSON scene hierarchy with buffers</span>
              </div>
              <div className="format-badge">
                <span className="format-ext">.OBJ + .MTL</span>
                <span className="format-desc">Wavefront polygon mesh & materials</span>
              </div>
              <div className="format-badge">
                <span className="format-ext">.SPLAT</span>
                <span className="format-desc">3D Gaussian Splatting radiance fields</span>
              </div>
            </div>

            {/* Workflow Diagram */}
            <div className="preservation-workflow-box mt-8">
              <h4 className="text-xs uppercase tracking-wider text-amber-400 font-semibold mb-3">
                Digital Preservation Intake Workflow
              </h4>
              <div className="workflow-steps-grid">
                <div className="workflow-step">
                  <div className="step-num">01</div>
                  <h5 className="step-title">Survey Capture</h5>
                  <p className="step-desc">LiDAR & aerial drone overlapping high-resolution imagery</p>
                </div>
                <div className="workflow-step">
                  <div className="step-num">02</div>
                  <h5 className="step-title">Point Cloud Generation</h5>
                  <p className="step-desc">Sub-millimeter structure-from-motion alignment</p>
                </div>
                <div className="workflow-step">
                  <div className="step-num">03</div>
                  <h5 className="step-title">Mesh & Texture Archival</h5>
                  <p className="step-desc">PBR material baking with spatial normal preservation</p>
                </div>
                <div className="workflow-step">
                  <div className="step-num">04</div>
                  <h5 className="step-title">SHA-256 Provenance</h5>
                  <p className="step-desc">Cryptographic checksum registered in PostgreSQL</p>
                </div>
              </div>
            </div>

            {/* Security note */}
            <div className="preservation-security-note mt-6">
              <Lock className="w-4 h-4 text-amber-400 mr-2 shrink-0" />
              <span className="text-xs text-gray-400">
                Registering new preservation models requires authenticated administrative credentials via the Preservation Management portal.
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Compact panel mode for dashboard
  return (
    <div className="bottom-panel-card three-d-panel">
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
            verified scans (GLB, GLTF, OBJ, SPLAT) under the Phase 4 preservation standard.
          </p>
          <div className="empty-state-actions">
            <button className="btn-empty-action" onClick={onExplore3D}>
              <UploadCloud className="w-3.5 h-3.5 mr-1.5 inline" />
              <span>Preservation Pipeline</span>
            </button>
            <span className="pipeline-status-badge">
              <ShieldCheck className="w-3 h-3 mr-1 inline text-emerald-400" />
              Ingestion Ready (0 Models)
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ThreeDExplorer;
