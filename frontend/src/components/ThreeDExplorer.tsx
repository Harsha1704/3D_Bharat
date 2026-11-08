import React from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Box,
  ArrowRight,
  ShieldCheck,
  Eye,
  RotateCw,
  Sparkles,
} from "lucide-react";
import type { Heritage3DAsset } from "../api";
import Heritage3DExplorerPage from "./Heritage3DExplorerPage";

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
  const navigate = useNavigate();
  const hasModels = assets3D.length > 0;
  const pilotModel = assets3D.find((a) => a.is_pilot) || assets3D[0];

  if (isFullPage) {
    return <Heritage3DExplorerPage />;
  }

  // Compact panel mode for Command Centre dashboard
  return (
    <div className="bottom-panel-card three-d-panel">
      <div className="panel-header">
        <div className="panel-title-group">
          <Box className="panel-icon text-amber-400" />
          <h3 className="panel-title">Interactive 3D Heritage Exploration</h3>
        </div>
        <Link
          to={pilotModel ? `/heritage/${pilotModel.heritage_site_id}/3d` : "/3d"}
          className="panel-action-link"
          onClick={() => {
            if (onExplore3D) onExplore3D();
          }}
        >
          <span>Launch 3D Viewer</span>
          <ArrowRight className="w-4 h-4 ml-1 inline" />
        </Link>
      </div>

      {hasModels && pilotModel ? (
        <div
          className="three-d-hero-card cursor-pointer group"
          onClick={() => navigate(`/heritage/${pilotModel.heritage_site_id}/3d`)}
        >
          <div className="relative p-5 bg-gradient-to-br from-[#0c1836] to-[#070d1e] rounded-xl border border-[#d4af37]/30 hover:border-[#d4af37]/60 transition-all shadow-xl">
            <div className="flex items-center justify-between mb-3">
              <span className="px-2.5 py-0.5 text-[10px] font-semibold tracking-wider text-amber-300 bg-amber-500/15 border border-amber-500/30 rounded-full uppercase flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                Pilot Monument • Konark Sun Temple
              </span>
              <span className="px-2 py-0.5 text-[10px] font-medium text-emerald-300 bg-emerald-500/15 border border-emerald-500/30 rounded-full flex items-center gap-1">
                <ShieldCheck className="w-3 h-3" />
                Verified glTF 2.0
              </span>
            </div>

            <h4 className="text-base font-bold text-white group-hover:text-amber-300 transition-colors">
              {pilotModel.title}
            </h4>
            <p className="text-xs text-slate-300 mt-1 line-clamp-2 leading-relaxed">
              {pilotModel.description}
            </p>

            <div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-800 text-xs">
              <div className="flex items-center gap-3 text-slate-400">
                <span>{(pilotModel.poly_count || pilotModel.polygon_count || 3332).toLocaleString()} Polygons</span>
                <span>•</span>
                <span>{(pilotModel.file_size_bytes / 1024).toFixed(1)} KB</span>
              </div>
              <div className="flex items-center gap-1.5 text-amber-400 font-medium group-hover:translate-x-0.5 transition-transform">
                <Eye className="w-3.5 h-3.5" />
                <span>Open in 3D</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="three-d-empty-state">
          <div className="empty-state-icon-ring">
            <Box className="w-8 h-8 text-amber-400" />
          </div>
          <h4 className="empty-state-title">3D Preservation Engine Ready</h4>
          <p className="empty-state-desc">
            Explore authentic 3D architectural models of India's world heritage monuments.
          </p>
          <div className="empty-state-actions">
            <Link to="/3d" className="btn-empty-action">
              <RotateCw className="w-3.5 h-3.5 mr-1.5 inline" />
              <span>Explore Pilot Monument</span>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};

export default ThreeDExplorer;
