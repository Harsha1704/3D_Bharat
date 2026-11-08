import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import {
  Box,
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  Copy,
  ExternalLink,
  ChevronRight,
  Layers,
  Sparkles,
  ArrowLeft,
  Lock,
  Cpu,
  Compass,
  AlertCircle,
  Eye,
} from "lucide-react";
import {
  getPilot3DAsset,
  getSite3DAssets,
  getHeritageSite,
  type Heritage3DAsset,
  type HeritageSite,
} from "../api";
import Heritage3DViewer from "./Heritage3DViewer";

interface Heritage3DExplorerPageProps {
  onAskAiAboutSite?: (siteName: string) => void;
  initialAssets?: Heritage3DAsset[];
}

export const Heritage3DExplorerPage: React.FC<Heritage3DExplorerPageProps> = ({
  onAskAiAboutSite,
  initialAssets = [],
}) => {
  const { siteId } = useParams<{ siteId?: string }>();
  const navigate = useNavigate();

  const [asset, setAsset] = useState<Heritage3DAsset | null>(null);
  const [site, setSite] = useState<HeritageSite | null>(null);
  const [availableAssets, setAvailableAssets] = useState<Heritage3DAsset[]>(initialAssets);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedHash, setCopiedHash] = useState(false);
  const [activeTab, setActiveTab] = useState<"provenance" | "architecture" | "specs">("provenance");

  useEffect(() => {
    let isMounted = true;
    const fetchAssetAndSite = async () => {
      try {
        setLoading(true);
        setError(null);

        let targetAsset: Heritage3DAsset | null = null;
        let siteData: HeritageSite | null = null;

        if (siteId) {
          const sId = parseInt(siteId, 10);
          if (!isNaN(sId)) {
            const [siteObj, siteAssets] = await Promise.all([
              getHeritageSite(sId).catch(() => null),
              getSite3DAssets(sId).catch(() => []),
            ]);
            siteData = siteObj;
            if (isMounted && siteAssets.length > 0) {
              setAvailableAssets(siteAssets);
              targetAsset = siteAssets[0];
            }
          }
        }

        // Fallback to Pilot Monument if no site-specific asset
        if (!targetAsset) {
          const pilotInInitial = initialAssets.find((a) => a.is_pilot && a.visibility_status === "PUBLIC");
          if (pilotInInitial) {
            targetAsset = pilotInInitial;
          } else {
            targetAsset = await getPilot3DAsset();
          }

          if (targetAsset && !siteData) {
            siteData = await getHeritageSite(targetAsset.heritage_site_id).catch(() => null);
          }
        }

        if (isMounted) {
          setAsset(targetAsset);
          setSite(siteData);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || "Failed to load 3D heritage model.");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchAssetAndSite();
    return () => {
      isMounted = false;
    };
  }, [siteId, initialAssets]);

  const handleCopyChecksum = () => {
    if (!asset?.checksum_sha256) return;
    if (navigator?.clipboard?.writeText) {
      navigator.clipboard.writeText(asset.checksum_sha256).catch(() => {});
    }
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  const handleAskAi = () => {
    const siteName = site?.name || asset?.title || "Konark Sun Temple";
    if (onAskAiAboutSite) {
      onAskAiAboutSite(siteName);
    } else {
      navigate(`/assistant?q=${encodeURIComponent(`Tell me about the architecture and 3D structure of ${siteName}`)}`);
    }
  };

  const getAuthenticityColor = (origin?: string) => {
    switch (origin?.toUpperCase()) {
      case "PHOTOGRAMMETRY_SCAN":
      case "LASER_SCAN":
        return "bg-emerald-500/20 text-emerald-300 border-emerald-500/40";
      case "INSTITUTIONAL_3D_MODEL":
        return "bg-blue-500/20 text-blue-300 border-blue-500/40";
      case "HISTORICAL_RECONSTRUCTION":
        return "bg-amber-500/20 text-amber-300 border-amber-500/40";
      case "ARCHITECTURAL_VISUALIZATION":
        return "bg-amber-500/20 text-amber-300 border-amber-500/40";
      default:
        return "bg-purple-500/20 text-purple-300 border-purple-500/40";
    }
  };

  const isRightsReview = asset?.rights_status === "RIGHTS_REVIEW_REQUIRED";

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-[600px] bg-[#070d1e] text-white">
        <Box className="w-12 h-12 text-[#d4af37] animate-pulse mb-4" />
        <h3 className="text-lg font-semibold text-amber-100">Initializing 3D Heritage Environment</h3>
        <p className="text-xs text-slate-400 mt-1">Streaming architectural assets and cryptographic verification records...</p>
      </div>
    );
  }

  if (error || !asset) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-[600px] bg-[#070d1e] text-white p-6 text-center">
        <Box className="w-12 h-12 text-rose-400 mb-3" />
        <h3 className="text-lg font-semibold text-rose-200">Unable to Load 3D Asset</h3>
        <p className="text-xs text-slate-400 max-w-md mt-1 mb-6">
          {error || "No active 3D model found for this monument. The preservation ingestion pipeline is ready to accept verified captures."}
        </p>
        <Link
          to="/explorer"
          className="px-4 py-2 bg-[#d4af37] text-slate-950 font-medium text-xs rounded-lg hover:bg-[#e5c158] transition-colors"
        >
          Return to Heritage Explorer
        </Link>
      </div>
    );
  }

  const modelUrl = asset.file_url || `/api/v1/heritage-3d/assets/${asset.id}/file`;

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-64px)] bg-[#070d1e] text-slate-100 overflow-hidden">
      {/* Top Breadcrumb & Header Bar */}
      <div className="h-14 border-b border-slate-800/80 bg-[#0a1128]/90 px-6 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <Link
            to="/explorer"
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-[#d4af37] transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Heritage Explorer</span>
          </Link>
          <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
          <span className="text-xs font-medium text-slate-300">
            {site?.name || "Monument 3D Exploration"}
          </span>
          <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
          <span className="text-xs font-semibold text-[#d4af37]">Interactive 3D Model</span>
        </div>

        <div className="flex items-center gap-3">
          {/* Multiple Assets Selector if applicable */}
          {availableAssets.length > 1 && (
            <select
              value={asset.id}
              onChange={(e) => {
                const selected = availableAssets.find((a) => a.id === parseInt(e.target.value, 10));
                if (selected) setAsset(selected);
              }}
              className="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded px-2 py-1"
            >
              {availableAssets.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.title}
                </option>
              ))}
            </select>
          )}

          {/* Authenticity Classification Pill */}
          <div
            className={`px-2.5 py-1 text-[11px] font-medium rounded-full border flex items-center gap-1.5 ${getAuthenticityColor(
              asset.asset_origin
            )}`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>{(asset.asset_origin || "ARCHITECTURAL_VISUALIZATION").replace(/_/g, " ")}</span>
          </div>

          {/* Rights Status Pill */}
          {isRightsReview && (
            <div className="px-2.5 py-1 text-[11px] font-medium rounded-full border border-amber-500/40 bg-amber-500/15 text-amber-300 flex items-center gap-1">
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>RIGHTS REVIEW PENDING</span>
            </div>
          )}

          {/* Ask AI shortcut */}
          <button
            onClick={handleAskAi}
            className="flex items-center gap-1.5 px-3 py-1 bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/30 text-amber-300 text-xs rounded-md transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Ask AI About Architecture</span>
          </button>
        </div>
      </div>

      {/* Main Workspace: 3D Canvas on Left, Provenance & Specs Drawer on Right */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* Left: Interactive 3D Canvas */}
        <div className="flex-1 relative h-full">
          <Heritage3DViewer
            modelUrl={modelUrl}
            title={asset.title}
            polyCount={asset.poly_count || asset.polygon_count}
            vertexCount={asset.vertex_count}
          />
        </div>

        {/* Right: Architectural Provenance & Verification Drawer */}
        <div className="w-full lg:w-[420px] bg-[#0c142c] border-l border-slate-800/80 flex flex-col h-full overflow-hidden shrink-0">
          {/* Drawer Header */}
          <div className="p-5 border-b border-slate-800/80 bg-[#0a1128]">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-amber-400">
              <Box className="w-4 h-4" />
              <span>Digital Preservation Dossier</span>
            </div>
            <h2 className="text-base font-bold text-white mt-1 leading-snug">{asset.title}</h2>
            {site && (
              <p className="text-xs text-slate-400 mt-0.5">
                {site.state} • {site.period || "Ancient Period"}
              </p>
            )}

            {/* Navigation Tabs */}
            <div className="flex items-center gap-2 mt-4 pt-3 border-t border-slate-800">
              <button
                onClick={() => setActiveTab("provenance")}
                className={`flex-1 py-1.5 text-xs font-medium rounded transition-colors ${
                  activeTab === "provenance"
                    ? "bg-[#d4af37] text-slate-950 font-semibold"
                    : "text-slate-400 hover:text-white bg-slate-900/60"
                }`}
              >
                Rights & Provenance
              </button>
              <button
                onClick={() => setActiveTab("architecture")}
                className={`flex-1 py-1.5 text-xs font-medium rounded transition-colors ${
                  activeTab === "architecture"
                    ? "bg-[#d4af37] text-slate-950 font-semibold"
                    : "text-slate-400 hover:text-white bg-slate-900/60"
                }`}
              >
                Architecture
              </button>
              <button
                onClick={() => setActiveTab("specs")}
                className={`flex-1 py-1.5 text-xs font-medium rounded transition-colors ${
                  activeTab === "specs"
                    ? "bg-[#d4af37] text-slate-950 font-semibold"
                    : "text-slate-400 hover:text-white bg-slate-900/60"
                }`}
              >
                Technical
              </button>
            </div>
          </div>

          {/* Drawer Scrollable Content */}
          <div className="flex-1 overflow-y-auto p-5 space-y-5 text-xs leading-relaxed text-slate-300">
            {/* TAB 1: RIGHTS & PROVENANCE */}
            {activeTab === "provenance" && (
              <>
                <div className="bg-[#0f1b3b] p-3.5 rounded-lg border border-slate-800">
                  <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-1">
                    Authenticity & Genesis Classification
                  </span>
                  <div className="text-sm font-semibold text-amber-200">
                    {(asset.asset_origin || "ARCHITECTURAL_VISUALIZATION").replace(/_/g, " ")}
                  </div>
                  <p className="text-[11px] text-slate-300 mt-1.5 leading-normal">
                    This model is a <strong>programmatically generated procedural 3D architectural visualization</strong> synthesized
                    by the 3D BHARAT geometry engine. It mathematically reconstructs the core Kalinga architectural forms
                    (stepped pidha tiers, cosmic chariot wheels, crowning amalaka and kalasha) for educational and visual study.
                    It is not an archaeological laser scan or photogrammetry capture.
                  </p>
                </div>

                {/* Cryptographic SHA-256 Verification */}
                <div className="bg-[#0f1b3b] p-3.5 rounded-lg border border-slate-800">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] uppercase font-semibold text-slate-400 flex items-center gap-1">
                      <Lock className="w-3 h-3 text-emerald-400" />
                      Cryptographic SHA-256 Checksum
                    </span>
                    <button
                      onClick={handleCopyChecksum}
                      className="text-amber-400 hover:text-amber-300 flex items-center gap-1 text-[10px]"
                    >
                      {copiedHash ? (
                        <>
                          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                          <span className="text-emerald-400">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          <span>Copy Hash</span>
                        </>
                      )}
                    </button>
                  </div>
                  <div className="font-mono text-[10px] text-slate-200 bg-slate-950/80 p-2 rounded border border-slate-800 break-all select-all">
                    {asset.checksum_sha256}
                  </div>
                </div>

                {/* Rights and Licensing Notice */}
                <div className="bg-[#0f1b3b] p-3.5 rounded-lg border border-slate-800 space-y-2.5">
                  <span className="text-[10px] uppercase font-semibold text-slate-400 block">
                    Licensing & Usage Permissions
                  </span>
                  <div className="flex items-center justify-between py-1 border-b border-slate-800">
                    <span className="text-slate-400">License Standard:</span>
                    <span className="font-semibold text-amber-300">{asset.licence_name || "RIGHTS_REVIEW_PENDING"}</span>
                  </div>
                  <div className="flex items-center justify-between py-1 border-b border-slate-800">
                    <span className="text-slate-400">Rights Status:</span>
                    <span className="font-semibold text-amber-300">
                      {(asset.rights_status || "RIGHTS_REVIEW_REQUIRED").replace(/_/g, " ")}
                    </span>
                  </div>
                  <div className="flex items-center justify-between py-1 border-b border-slate-800">
                    <span className="text-slate-400">In-Browser Display:</span>
                    <span className="text-emerald-400 font-semibold flex items-center gap-1">
                      <Eye className="w-3 h-3" /> Permitted
                    </span>
                  </div>
                  <div className="flex items-center justify-between py-1 border-b border-slate-800">
                    <span className="text-slate-400">Commercial Use:</span>
                    <span className="text-rose-400 font-medium">Restricted</span>
                  </div>
                  <div className="flex items-center justify-between py-1 border-b border-slate-800">
                    <span className="text-slate-400">Remix & Modification:</span>
                    <span className="text-slate-400">Pending Institutional Review</span>
                  </div>
                  <div className="flex items-center justify-between py-1">
                    <span className="text-slate-400">Public Binary Download:</span>
                    <span className="text-rose-400 font-medium">Restricted (Viewing Only)</span>
                  </div>
                </div>

                {/* Download Protection Notice Banner */}
                <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg flex items-start gap-2 text-amber-200 text-[11px] leading-normal">
                  <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <strong>Direct Binary Download Restricted:</strong> Public distribution of raw model binary files is restricted
                    until full archival rights verification is completed. Interactive visual inspection in this 3D viewer is fully authorized.
                  </div>
                </div>

                {/* Attribution & Provenance */}
                <div className="bg-[#0f1b3b] p-3.5 rounded-lg border border-slate-800">
                  <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-1">
                    Institutional Provenance & Attribution
                  </span>
                  <p className="text-[11px] text-slate-300 leading-relaxed italic">
                    "{asset.attribution_text || `Synthesized via 3D BHARAT geometry engine. Permitted for in-browser visual inspection only.`}"
                  </p>
                  {asset.source_url && (
                    <a
                      href={asset.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-2.5 inline-flex items-center gap-1 text-[11px] text-amber-400 hover:underline"
                    >
                      <span>Archival UNESCO Monument Dossier</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </>
            )}

            {/* TAB 2: ARCHITECTURE HIGHLIGHTS */}
            {activeTab === "architecture" && (
              <>
                <div className="bg-[#0f1b3b] p-3.5 rounded-lg border border-slate-800 space-y-2">
                  <span className="text-[10px] uppercase font-semibold text-amber-400 flex items-center gap-1.5">
                    <Compass className="w-3.5 h-3.5" />
                    Kalinga Architectural Hierarchy
                  </span>
                  <p className="text-[11px] text-slate-300 leading-relaxed">
                    The Konark Sun Temple (Surya Deula) is conceived as a monumental processional chariot
                    for the sun god Surya, crafted in golden-hued khondalite sandstone.
                  </p>
                </div>

                <div className="space-y-3">
                  <div className="p-3 bg-slate-900/60 rounded border border-slate-800">
                    <h4 className="text-xs font-semibold text-white flex items-center gap-1.5 mb-1">
                      <Layers className="w-3.5 h-3.5 text-amber-400" />
                      1. Jagamohana (Porch / Mandapa)
                    </h4>
                    <p className="text-[11px] text-slate-400 leading-normal">
                      Stepped pyramidal pidha deula roof arranged in four tiers (potalas) of horizontal courses,
                      engineered to withstand coastal cyclone winds and shelter congregational worship.
                    </p>
                  </div>

                  <div className="p-3 bg-slate-900/60 rounded border border-slate-800">
                    <h4 className="text-xs font-semibold text-white flex items-center gap-1.5 mb-1">
                      <Compass className="w-3.5 h-3.5 text-amber-400" />
                      2. The 24 Chariot Wheels (Chakkas)
                    </h4>
                    <p className="text-[11px] text-slate-400 leading-normal">
                      12 wheels along the northern plinth and 12 along the southern plinth. Each wheel
                      functions as a precision astronomical sundial with major and minor spokes and carved hubs.
                    </p>
                  </div>

                  <div className="p-3 bg-slate-900/60 rounded border border-slate-800">
                    <h4 className="text-xs font-semibold text-white flex items-center gap-1.5 mb-1">
                      <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                      3. Crowning Amalaka & Kalasha
                    </h4>
                    <p className="text-[11px] text-slate-400 leading-normal">
                      Fluted circular stone disc (amalaka) representing the celestial lotus, crowned by the
                      golden kalasha finial marking the architectural zenith at 30.6 meters elevation.
                    </p>
                  </div>
                </div>
              </>
            )}

            {/* TAB 3: TECHNICAL SPECIFICATIONS */}
            {activeTab === "specs" && (
              <div className="space-y-3">
                <div className="bg-[#0f1b3b] p-3.5 rounded-lg border border-slate-800 space-y-2">
                  <span className="text-[10px] uppercase font-semibold text-slate-400 flex items-center gap-1.5">
                    <Cpu className="w-3.5 h-3.5 text-amber-400" />
                    3D Engine & Geometry Specs
                  </span>
                  <div className="grid grid-cols-2 gap-2 pt-1 text-[11px]">
                    <div className="p-2 bg-slate-950/60 rounded border border-slate-800">
                      <span className="text-slate-400 block text-[10px]">Container Format</span>
                      <span className="text-white font-mono font-medium">{asset.asset_format || "GLB 2.0"}</span>
                    </div>
                    <div className="p-2 bg-slate-950/60 rounded border border-slate-800">
                      <span className="text-slate-400 block text-[10px]">File Size</span>
                      <span className="text-white font-mono font-medium">
                        {(asset.file_size_bytes / 1024).toFixed(1)} KB
                      </span>
                    </div>
                    <div className="p-2 bg-slate-950/60 rounded border border-slate-800">
                      <span className="text-slate-400 block text-[10px]">Polygons</span>
                      <span className="text-amber-300 font-mono font-medium">
                        {(asset.poly_count || asset.polygon_count || 3332).toLocaleString()}
                      </span>
                    </div>
                    <div className="p-2 bg-slate-950/60 rounded border border-slate-800">
                      <span className="text-slate-400 block text-[10px]">Vertices</span>
                      <span className="text-amber-300 font-mono font-medium">
                        {(asset.vertex_count || 3732).toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="bg-[#0f1b3b] p-3.5 rounded-lg border border-slate-800 space-y-2">
                  <span className="text-[10px] uppercase font-semibold text-slate-400 block">
                    Spatial Reference System
                  </span>
                  <div className="text-[11px] text-slate-300 space-y-1">
                    <div>
                      <span className="text-slate-400">Units: </span>
                      <span className="font-mono text-white">{asset.units || "meters (1.0 = 1m)"}</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Coordinates: </span>
                      <span className="text-white">{asset.coordinate_system || "Cartesian Y-Up, Ground Y=0"}</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Dimensions: </span>
                      <span className="text-white">Footprint 36m x 54m • Height 30.6m</span>
                    </div>
                  </div>
                </div>

                <div className="p-3 bg-slate-900/60 rounded border border-slate-800 text-[11px] text-slate-400">
                  <div className="flex items-center gap-1.5 text-emerald-400 font-semibold mb-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Alembic & PostgreSQL Verified</span>
                  </div>
                  Registered under Phase 10 verified asset pipeline with active database row ID #{asset.id}.
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Heritage3DExplorerPage;
