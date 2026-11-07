import React, { useState, useEffect, useMemo, useRef } from "react";
import {
  Network,
  ArrowRight,
  Landmark,
  Crown,
  User,
  Calendar,
  Layers,
  BookOpen,
  ExternalLink,
  Search,
  Filter,
  X,
  Sparkles,
  Info,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Loader2,
} from "lucide-react";
import {
  exploreCulturalGraph,
  getCulturalGraphStatistics,
  getCulturalEntityProvenance,
  searchCulturalEntities,
  type HeritageSite,
  type CulturalGraphEntity,
  type CulturalGraphRelationship,
  type CulturalGraphStatistics,
  type CulturalGraphProvenanceResponse,
} from "../api";

interface KnowledgeGraphViewProps {
  selectedSite: HeritageSite | null;
  allSites: HeritageSite[];
  connections?: any[];
  onSelectConnectedSite: (site: HeritageSite) => void;
  onViewFullGraph: () => void;
  isExpanded?: boolean;
  onOpenSiteDossier?: (site: HeritageSite) => void;
}

// Visual themes for the 6 cultural entity types
const ENTITY_TYPE_CONFIG: Record<
  string,
  { label: string; color: string; bgColor: string; borderColor: string; icon: any }
> = {
  HERITAGE_SITE: {
    label: "Heritage Site",
    color: "#F59E0B",
    bgColor: "rgba(245, 158, 11, 0.15)",
    borderColor: "#F59E0B",
    icon: Landmark,
  },
  DYNASTY: {
    label: "Dynasty",
    color: "#A78BFA",
    bgColor: "rgba(167, 139, 250, 0.15)",
    borderColor: "#A78BFA",
    icon: Crown,
  },
  HISTORICAL_PERSON: {
    label: "Historical Person",
    color: "#38BDF8",
    bgColor: "rgba(56, 189, 248, 0.15)",
    borderColor: "#38BDF8",
    icon: User,
  },
  HISTORICAL_EVENT: {
    label: "Historical Event",
    color: "#FB923C",
    bgColor: "rgba(251, 146, 60, 0.15)",
    borderColor: "#FB923C",
    icon: Calendar,
  },
  ARCHITECTURAL_STYLE: {
    label: "Architectural Style",
    color: "#34D399",
    bgColor: "rgba(52, 211, 153, 0.15)",
    borderColor: "#34D399",
    icon: Layers,
  },
  CULTURAL_TRADITION: {
    label: "Cultural Tradition",
    color: "#F472B6",
    bgColor: "rgba(244, 114, 182, 0.15)",
    borderColor: "#F472B6",
    icon: BookOpen,
  },
};

export const KnowledgeGraphView: React.FC<KnowledgeGraphViewProps> = ({
  selectedSite,
  allSites,
  onSelectConnectedSite,
  onViewFullGraph,
  isExpanded = false,
  onOpenSiteDossier,
}) => {
  // Graph Data State
  const [centerEntity, setCenterEntity] = useState<CulturalGraphEntity | null>(null);
  const [nodes, setNodes] = useState<CulturalGraphEntity[]>([]);
  const [edges, setEdges] = useState<CulturalGraphRelationship[]>([]);
  const [stats, setStats] = useState<CulturalGraphStatistics | null>(null);
  const [loading, setLoading] = useState(false);

  // Filters & Controls
  const [depth, setDepth] = useState<number>(1);
  const [selectedTypeFilter, setSelectedTypeFilter] = useState<string>("ALL");
  const [evidenceOnlyFilter, setEvidenceOnlyFilter] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<CulturalGraphEntity[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Provenance / Details Drawer State
  const [inspectedEntity, setInspectedEntity] = useState<CulturalGraphEntity | null>(null);
  const [provenanceData, setProvenanceData] = useState<CulturalGraphProvenanceResponse | null>(null);
  const [provenanceLoading, setProvenanceLoading] = useState(false);

  // Canvas / Pan-Zoom State
  const [zoomLevel, setZoomLevel] = useState(1);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const dragStart = useRef({ x: 0, y: 0 });

  // 1. Load initial graph statistics
  useEffect(() => {
    let mounted = true;
    getCulturalGraphStatistics()
      .then((data) => {
        if (mounted) setStats(data);
      })
      .catch(() => {});
    return () => {
      mounted = false;
    };
  }, []);

  // 2. Center on the currently selected site or Taj Mahal default
  useEffect(() => {
    let mounted = true;
    const initialSiteName = selectedSite?.name || "Taj Mahal";

    searchCulturalEntities(initialSiteName, "HERITAGE_SITE", 1)
      .then((res) => {
        if (mounted && res.length > 0) {
          setCenterEntity(res[0]);
        }
      })
      .catch(() => {});

    return () => {
      mounted = false;
    };
  }, [selectedSite]);

  // 3. Fetch sub-graph whenever center entity, depth, or filters change
  useEffect(() => {
    if (!centerEntity) return;
    let mounted = true;
    setLoading(true);

    const typeFilter = selectedTypeFilter !== "ALL" ? [selectedTypeFilter] : undefined;
    const evidenceFilter = evidenceOnlyFilter ? "DOCUMENTED" : undefined;

    exploreCulturalGraph(centerEntity.id, {
      depth: isExpanded ? depth : 1,
      entity_types: typeFilter,
      evidence_status: evidenceFilter,
      limit: isExpanded ? 50 : 8,
    })
      .then((res) => {
        if (mounted) {
          setNodes(res.nodes);
          setEdges(res.edges);
          setLoading(false);
        }
      })
      .catch(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [centerEntity, depth, selectedTypeFilter, evidenceOnlyFilter, isExpanded]);

  // 4. Handle Search queries
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }
    const timer = setTimeout(() => {
      setIsSearching(true);
      searchCulturalEntities(searchQuery.trim(), undefined, 6)
        .then((res) => {
          setSearchResults(res);
          setIsSearching(false);
        })
        .catch(() => setIsSearching(false));
    }, 250);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // 5. Inspect entity & fetch provenance dossier
  const handleInspectEntity = (entity: CulturalGraphEntity) => {
    setInspectedEntity(entity);
    setProvenanceLoading(true);
    getCulturalEntityProvenance(entity.id)
      .then((res) => {
        setProvenanceData(res);
        setProvenanceLoading(false);
      })
      .catch(() => {
        setProvenanceLoading(false);
      });
  };

  // 6. Center graph on an entity
  const handleSetCenter = (entity: CulturalGraphEntity) => {
    setCenterEntity(entity);
    setSearchQuery("");
    setSearchResults([]);
    setPanOffset({ x: 0, y: 0 });
    setZoomLevel(1);
    // If it's a heritage site, sync with parent dashboard
    if (entity.heritage_site_id) {
      const matchedSite = allSites.find((s) => s.id === entity.heritage_site_id);
      if (matchedSite) onSelectConnectedSite(matchedSite);
    }
  };

  // Node Positions calculation (Orbital distribution around center)
  const nodePositions = useMemo(() => {
    if (!centerEntity) return new Map<number, { x: number; y: number }>();
    const posMap = new Map<number, { x: number; y: number }>();

    // Center is at 0, 0
    posMap.set(centerEntity.id, { x: 0, y: 0 });

    const satellites = nodes.filter((n) => n.id !== centerEntity.id);
    const count = satellites.length;
    if (count === 0) return posMap;

    // Multi-orbit concentric distribution to prevent node overlap & canvas clipping
    const baseRadius = isExpanded ? 190 : 115;
    const outerRadius = isExpanded ? 260 : 145;
    satellites.forEach((node, i) => {
      const isStaggered = count > 5 && i % 2 === 1;
      const r = isStaggered ? outerRadius : baseRadius;
      const angle = (2 * Math.PI * i) / count - Math.PI / 2;
      const x = Math.round(r * Math.cos(angle));
      const y = Math.round(r * Math.sin(angle));
      posMap.set(node.id, { x, y });
    });

    return posMap;
  }, [centerEntity, nodes, isExpanded]);

  // Pan / Drag handlers for expanded mode
  const handleMouseDown = (e: React.MouseEvent) => {
    if (!isExpanded) return;
    setIsDragging(true);
    dragStart.current = { x: e.clientX - panOffset.x, y: e.clientY - panOffset.y };
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setPanOffset({
      x: e.clientX - dragStart.current.x,
      y: e.clientY - dragStart.current.y,
    });
  };

  const handleMouseUp = () => setIsDragging(false);

  return (
    <div className={`graph-panel-card cultural-knowledge-graph ${isExpanded ? "expanded-mode" : ""}`}>
      {/* PANEL HEADER */}
      <div className="panel-header">
        <div className="panel-title-group">
          <Network className="panel-icon text-amber-400" />
          <div>
            <h3 className="panel-title flex items-center gap-2">
              <span>{isExpanded ? "National Cultural Knowledge Graph" : "Knowledge Graph"}</span>
              {loading && <Loader2 className="w-3.5 h-3.5 animate-spin text-amber-400 inline" />}
            </h3>
            {stats && (
              <span className="graph-stats-subtext">
                {stats.total_entities} Entities • {stats.total_relationships} Relationships
              </span>
            )}
          </div>
        </div>

        {!isExpanded && (
          <button className="panel-action-link" onClick={onViewFullGraph}>
            <span>View Graph</span>
            <ArrowRight className="w-4 h-4 ml-1 inline" />
          </button>
        )}
      </div>

      {/* EXPANDED TOOLBAR: SEARCH & FILTERS */}
      {isExpanded && (
        <div className="graph-controls-bar">
          {/* Search Box */}
          <div className="graph-search-container">
            {isSearching ? (
              <Loader2 className="w-4 h-4 animate-spin text-amber-400" />
            ) : (
              <Search className="w-4 h-4 text-gray-400" />
            )}
            <input
              type="text"
              className="graph-search-input"
              placeholder="Search dynasty, ruler, monument, style..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <button
                className="clear-search-btn"
                onClick={() => {
                  setSearchQuery("");
                  setSearchResults([]);
                }}
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}

            {/* Live Search Autocomplete */}
            {searchResults.length > 0 && (
              <div className="graph-search-dropdown">
                {searchResults.map((result) => {
                  const cfg = ENTITY_TYPE_CONFIG[result.entity_type] || ENTITY_TYPE_CONFIG.HERITAGE_SITE;
                  const Icon = cfg.icon;
                  return (
                    <div
                      key={result.id}
                      className="search-result-item"
                      onClick={() => handleSetCenter(result)}
                    >
                      <Icon className="w-4 h-4" style={{ color: cfg.color }} />
                      <div className="search-result-text">
                        <span className="result-name">{result.canonical_name}</span>
                        <span className="result-type" style={{ color: cfg.color }}>
                          {cfg.label}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Entity Type Filter */}
          <div className="graph-filter-group">
            <span className="filter-label">
              <Filter className="w-3.5 h-3.5 inline mr-1 text-amber-400" /> Type:
            </span>
            <select
              className="graph-filter-select"
              value={selectedTypeFilter}
              onChange={(e) => setSelectedTypeFilter(e.target.value)}
            >
              <option value="ALL">All Types</option>
              <option value="HERITAGE_SITE">Monuments</option>
              <option value="DYNASTY">Dynasties</option>
              <option value="HISTORICAL_PERSON">Rulers & Figures</option>
              <option value="ARCHITECTURAL_STYLE">Architectural Styles</option>
              <option value="CULTURAL_TRADITION">Traditions</option>
            </select>
          </div>

          {/* Depth Control */}
          <div className="graph-filter-group">
            <span className="filter-label">Depth:</span>
            <div className="depth-buttons-group">
              {[1, 2, 3].map((d) => (
                <button
                  key={d}
                  className={`btn-depth ${depth === d ? "active" : ""}`}
                  onClick={() => setDepth(d)}
                >
                  {d} Hop{d > 1 ? "s" : ""}
                </button>
              ))}
            </div>
          </div>

          {/* Documented Evidence Only Toggle */}
          <label className="evidence-filter-toggle">
            <input
              type="checkbox"
              checked={evidenceOnlyFilter}
              onChange={(e) => setEvidenceOnlyFilter(e.target.checked)}
            />
            <span>Documented Sources Only</span>
          </label>

          {/* Pan & Zoom Controls */}
          <div className="pan-zoom-controls">
            <button
              className="btn-zoom"
              title="Zoom In"
              onClick={() => setZoomLevel((z) => Math.min(z + 0.2, 2.0))}
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              className="btn-zoom"
              title="Zoom Out"
              onClick={() => setZoomLevel((z) => Math.max(z - 0.2, 0.6))}
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <button
              className="btn-zoom"
              title="Reset View"
              onClick={() => {
                setZoomLevel(1);
                setPanOffset({ x: 0, y: 0 });
              }}
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* GRAPH CANVAS CONTAINER */}
      <div
        className={`radial-graph-container ${isExpanded ? "expanded-canvas" : ""}`}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{ cursor: isExpanded ? (isDragging ? "grabbing" : "grab") : "default" }}
      >
        {centerEntity ? (
          <div
            className="graph-transform-layer"
            style={{
              transform: `translate(${panOffset.x}px, ${panOffset.y}px) scale(${zoomLevel})`,
              transition: isDragging ? "none" : "transform 0.15s ease-out",
            }}
          >
            {/* SVG Connecting Edges */}
            <svg
              className="radial-beams-svg"
              style={{
                width: isExpanded ? "1200px" : "100%",
                height: isExpanded ? "700px" : "100%",
                left: isExpanded ? "-600px" : "0",
                top: isExpanded ? "-350px" : "0",
                position: "absolute",
                pointerEvents: "none",
              }}
              viewBox={isExpanded ? "-600 -350 1200 700" : "-200 -200 400 400"}
            >
              <defs>
                <linearGradient id="edgeGradGold" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stopColor="#D9A441" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="#FFC857" stopOpacity="0.4" />
                </linearGradient>
                <marker
                  id="arrowGold"
                  viewBox="0 0 10 10"
                  refX="18"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 0 L 10 5 L 0 10 z" fill="#D9A441" />
                </marker>
              </defs>

              {edges.map((edge) => {
                const srcPos = nodePositions.get(edge.source_entity_id);
                const tgtPos = nodePositions.get(edge.target_entity_id);
                if (!srcPos || !tgtPos) return null;

                const isDocumented =
                  edge.evidence_status === "DOCUMENTED" || edge.evidence_status === "VERIFIED";

                return (
                  <g key={edge.id} className="graph-edge-group">
                    <line
                      x1={srcPos.x}
                      y1={srcPos.y}
                      x2={tgtPos.x}
                      y2={tgtPos.y}
                      stroke={isDocumented ? "url(#edgeGradGold)" : "#38BDF8"}
                      strokeWidth={isDocumented ? 2 : 1.5}
                      strokeDasharray={isDocumented ? "none" : "4 3"}
                      strokeOpacity={isDocumented ? 0.75 : 0.5}
                    />
                    {isExpanded && (
                      <text
                        x={(srcPos.x + tgtPos.x) / 2}
                        y={(srcPos.y + tgtPos.y) / 2 - 4}
                        fill="#D9A441"
                        fontSize="9"
                        textAnchor="middle"
                        className="edge-label-text"
                      >
                        {edge.relationship_type.replace(/_/g, " ")}
                      </text>
                    )}
                  </g>
                );
              })}
            </svg>

            {/* Central Hub Node */}
            {(() => {
              const cfg =
                ENTITY_TYPE_CONFIG[centerEntity.entity_type] ||
                ENTITY_TYPE_CONFIG.HERITAGE_SITE;
              const Icon = cfg.icon;
              return (
                <div
                  className="central-hub-node interactive"
                  onClick={() => handleInspectEntity(centerEntity)}
                  title={`Inspect ${centerEntity.canonical_name}`}
                >
                  <div
                    className="center-node-outer-glow"
                    style={{ borderColor: cfg.borderColor }}
                  >
                    <div
                      className="center-node-circle"
                      style={{ background: cfg.bgColor }}
                    >
                      <Icon className="w-7 h-7" style={{ color: cfg.color }} />
                    </div>
                  </div>
                  <span className="center-node-label">{centerEntity.canonical_name}</span>
                  <span className="center-node-type" style={{ color: cfg.color }}>
                    {cfg.label}
                  </span>
                </div>
              );
            })()}

            {/* Orbital Satellite Nodes */}
            {nodes
              .filter((n) => n.id !== centerEntity.id)
              .map((node) => {
                const pos = nodePositions.get(node.id) || { x: 0, y: 0 };
                const cfg =
                  ENTITY_TYPE_CONFIG[node.entity_type] ||
                  ENTITY_TYPE_CONFIG.HERITAGE_SITE;
                const Icon = cfg.icon;

                return (
                  <div
                    key={node.id}
                    className="orbital-node interactive"
                    style={{
                      transform: `translate(${pos.x}px, ${pos.y}px)`,
                    }}
                    onClick={() => handleInspectEntity(node)}
                    title={`Click to inspect details & provenance for ${node.canonical_name}`}
                  >
                    <div
                      className="orbital-node-circle"
                      style={{
                        borderColor: cfg.borderColor,
                        backgroundColor: "#0d1527",
                        boxShadow: `0 0 10px ${cfg.borderColor}40`,
                      }}
                    >
                      <Icon className="w-4 h-4" style={{ color: cfg.color }} />
                    </div>
                    <span className="orbital-node-label">{node.canonical_name}</span>
                    <span
                      className="orbital-node-rel-badge"
                      style={{
                        borderColor: `${cfg.borderColor}60`,
                        color: cfg.color,
                      }}
                    >
                      {cfg.label}
                    </span>
                  </div>
                );
              })}
          </div>
        ) : (
          <div className="graph-empty-state">
            <Network className="w-8 h-8 text-amber-400/60 mb-2" />
            <h5 className="text-white font-semibold text-sm">
              Loading Cultural Knowledge Graph...
            </h5>
          </div>
        )}
      </div>

      {/* SLIDE-OUT PROVENANCE & DETAILS DRAWER */}
      {inspectedEntity && (
        <div className="entity-provenance-drawer">
          <div className="drawer-header">
            <div className="drawer-title-group">
              {(() => {
                const cfg =
                  ENTITY_TYPE_CONFIG[inspectedEntity.entity_type] ||
                  ENTITY_TYPE_CONFIG.HERITAGE_SITE;
                const Icon = cfg.icon;
                return (
                  <div className="flex items-center gap-2">
                    <Icon className="w-5 h-5" style={{ color: cfg.color }} />
                    <div>
                      <h4 className="drawer-entity-name">
                        {inspectedEntity.canonical_name}
                      </h4>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span
                          className="entity-badge"
                          style={{
                            color: cfg.color,
                            backgroundColor: cfg.bgColor,
                            borderColor: cfg.borderColor,
                          }}
                        >
                          {cfg.label}
                        </span>
                        <span className="status-pill documented">
                          {inspectedEntity.verification_status}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })()}
            </div>

            <button
              className="drawer-close-btn"
              onClick={() => {
                setInspectedEntity(null);
                setProvenanceData(null);
              }}
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="drawer-content">
            {/* Quick Actions */}
            <div className="drawer-actions-row">
              <button
                className="btn-drawer-action"
                onClick={() => handleSetCenter(inspectedEntity)}
              >
                <Sparkles className="w-3.5 h-3.5 text-amber-400 mr-1" />
                Explore from Here
              </button>

              {inspectedEntity.heritage_site_id && onOpenSiteDossier && (
                <button
                  className="btn-drawer-action primary"
                  onClick={() => {
                    const site = allSites.find(
                      (s) => s.id === inspectedEntity.heritage_site_id
                    );
                    if (site) onOpenSiteDossier(site);
                  }}
                >
                  <Landmark className="w-3.5 h-3.5 mr-1" />
                  View Monument Dossier
                </button>
              )}
            </div>

            {/* Description & Context */}
            {inspectedEntity.description && (
              <div className="drawer-section">
                <span className="drawer-section-title">Historical Overview</span>
                <p className="drawer-description">{inspectedEntity.description}</p>
              </div>
            )}

            <div className="drawer-meta-grid">
              {inspectedEntity.period && (
                <div className="meta-box">
                  <span className="meta-box-label">Era / Period</span>
                  <span className="meta-box-val">{inspectedEntity.period}</span>
                </div>
              )}
              {inspectedEntity.geographical_context && (
                <div className="meta-box">
                  <span className="meta-box-label">Geographical Context</span>
                  <span className="meta-box-val">
                    {inspectedEntity.geographical_context}
                  </span>
                </div>
              )}
            </div>

            {/* Provenance & Citation Trail */}
            <div className="drawer-section mt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="drawer-section-title">
                  Evidence & Relationship Provenance
                </span>
                <Info className="w-3.5 h-3.5 text-gray-400" />
              </div>

              {provenanceLoading ? (
                <div className="provenance-loading">Loading citations...</div>
              ) : provenanceData && provenanceData.relationships_provenance.length > 0 ? (
                <div className="provenance-items-list">
                  {provenanceData.relationships_provenance.map((item) => {
                    const connCfg =
                      ENTITY_TYPE_CONFIG[item.connected_entity_type] ||
                      ENTITY_TYPE_CONFIG.HERITAGE_SITE;
                    return (
                      <div
                        key={item.relationship_id}
                        className="provenance-card"
                      >
                        <div className="provenance-rel-header">
                          <span className="prov-rel-type">
                            {item.relationship_type.replace(/_/g, " ")}
                          </span>
                          <span
                            className={`prov-evidence-badge ${item.evidence_status.toLowerCase()}`}
                          >
                            {item.evidence_status}
                          </span>
                        </div>

                        <div className="provenance-connected-target">
                          <span className="target-arrow">↳</span>
                          <span
                            className="target-name"
                            style={{ color: connCfg.color }}
                          >
                            {item.connected_entity_name}
                          </span>
                          <span className="target-type-label">
                            ({connCfg.label})
                          </span>
                        </div>

                        {/* Citation / Source Info */}
                        {(item.source_title || item.source_citation) && (
                          <div className="provenance-source-box">
                            {item.source_title && (
                              <div className="source-title-line">
                                <strong>Source:</strong> {item.source_title}
                              </div>
                            )}
                            {item.source_citation && (
                              <div className="source-citation-line">
                                {item.source_citation}
                              </div>
                            )}
                            {item.source_url && (
                              <a
                                href={item.source_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="source-link"
                              >
                                View Primary Archival Record{" "}
                                <ExternalLink className="w-3 h-3 ml-1" />
                              </a>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="provenance-empty">
                  No explicit external source records linked to these connections yet.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default KnowledgeGraphView;
