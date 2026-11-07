import React, { useMemo } from "react";
import { Network, ArrowRight } from "lucide-react";
import type { HeritageSite, HeritageConnection } from "../api";

interface KnowledgeGraphViewProps {
  selectedSite: HeritageSite | null;
  allSites: HeritageSite[];
  connections: HeritageConnection[];
  onSelectConnectedSite: (site: HeritageSite) => void;
  onViewFullGraph: () => void;
}

interface OrbitalNode {
  id: string | number;
  label: string;
  type: "site" | "tradition" | "architecture" | "person" | "region";
  imgUrl?: string;
  targetSite?: HeritageSite;
}

export const KnowledgeGraphView: React.FC<KnowledgeGraphViewProps> = ({
  selectedSite,
  allSites,
  connections,
  onSelectConnectedSite,
  onViewFullGraph,
}) => {
  // If no site selected, pick first site with connections or first site
  const currentSite = selectedSite || allSites[0] || null;

  // Build 4-6 dynamic orbital nodes related to currentSite
  const orbitalNodes = useMemo<OrbitalNode[]>(() => {
    if (!currentSite) return [];

    const nodes: OrbitalNode[] = [];

    // 1. Direct connections from DB
    const directConnections = connections.filter(
      (c) =>
        c.source_site_id === currentSite.id || c.target_site_id === currentSite.id
    );

    for (const conn of directConnections) {
      const otherId =
        conn.source_site_id === currentSite.id
          ? conn.target_site_id
          : conn.source_site_id;
      const otherSite = allSites.find((s) => s.id === otherId);
      if (otherSite && !nodes.some((n) => n.id === otherSite.id)) {
        nodes.push({
          id: otherSite.id,
          label: otherSite.name,
          type: "site",
          targetSite: otherSite,
        });
      }
    }

    // 2. Traditions or associated people
    if (currentSite.traditions && currentSite.traditions.length > 0) {
      for (const t of currentSite.traditions.slice(0, 2)) {
        if (!nodes.some((n) => n.label === t)) {
          nodes.push({
            id: `trad-${t}`,
            label: t,
            type: "tradition",
          });
        }
      }
    }

    // 3. Alternative names or period
    if (
      currentSite.alternative_names &&
      currentSite.alternative_names.length > 0
    ) {
      for (const alt of currentSite.alternative_names.slice(0, 1)) {
        if (!nodes.some((n) => n.label === alt)) {
          nodes.push({
            id: `alt-${alt}`,
            label: alt,
            type: "site",
          });
        }
      }
    }

    // 4. District / State Heritage
    if (currentSite.district || currentSite.state) {
      const locLabel = `${currentSite.district || currentSite.state} Heritage`;
      if (!nodes.some((n) => n.label === locLabel)) {
        nodes.push({
          id: `loc-${locLabel}`,
          label: locLabel,
          type: "region",
        });
      }
    }

    // Fallback orbital nodes matching the reference if site has few linkages
    const defaultLabels = [
      "Harmandir Sahib",
      "Jallianwala Bagh",
      "Punjab Culture",
      "Amritsar Heritage",
    ];

    while (nodes.length < 4) {
      const fallbackLabel = defaultLabels[nodes.length % defaultLabels.length];
      if (!nodes.some((n) => n.label === fallbackLabel)) {
        nodes.push({
          id: `fallback-${nodes.length}`,
          label: fallbackLabel,
          type: "tradition",
        });
      } else {
        nodes.push({
          id: `extra-${nodes.length}`,
          label: `${currentSite.category || "Monument"} Legacy`,
          type: "architecture",
        });
      }
    }

    return nodes.slice(0, 4);
  }, [currentSite, connections, allSites]);

  // Polar coordinate positions for 4 satellites: Top-Left, Top-Right, Bottom-Right, Bottom-Left
  const satellitePositions = [
    { top: "16%", left: "18%" },
    { top: "16%", right: "18%" },
    { bottom: "16%", right: "18%" },
    { bottom: "16%", left: "18%" },
  ];

  return (
    <div className="graph-panel-card">
      {/* Panel Header */}
      <div className="panel-header">
        <div className="panel-title-group">
          <Network className="panel-icon text-amber-400" />
          <h3 className="panel-title">Knowledge Graph</h3>
        </div>
        <button className="panel-action-link" onClick={onViewFullGraph}>
          <span>View Graph</span>
          <ArrowRight className="w-4 h-4 ml-1 inline" />
        </button>
      </div>

      {/* Radial Hub and Spoke Canvas */}
      <div className="radial-graph-container">
        {/* SVG Connecting Light Rays */}
        <svg
          className="radial-beams-svg"
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
        >
          {/* Beams from Center (50, 50) to 4 orbital quadrants */}
          <line
            x1="50"
            y1="50"
            x2="24"
            y2="24"
            stroke="url(#beamGrad)"
            strokeWidth="1.5"
            strokeDasharray="3 2"
          />
          <line
            x1="50"
            y1="50"
            x2="76"
            y2="24"
            stroke="url(#beamGrad)"
            strokeWidth="1.5"
            strokeDasharray="3 2"
          />
          <line
            x1="50"
            y1="50"
            x2="76"
            y2="76"
            stroke="url(#beamGrad)"
            strokeWidth="1.5"
            strokeDasharray="3 2"
          />
          <line
            x1="50"
            y1="50"
            x2="24"
            y2="76"
            stroke="url(#beamGrad)"
            strokeWidth="1.5"
            strokeDasharray="3 2"
          />

          <defs>
            <linearGradient id="beamGrad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#FFC857" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#D9A441" stopOpacity="0.3" />
            </linearGradient>
          </defs>
        </svg>

        {/* Central Hub Node */}
        {currentSite && (
          <div className="central-hub-node">
            <div className="center-node-outer-glow">
              <div className="center-node-circle">
                <img
                  src="https://images.unsplash.com/photo-1588096344356-9a425330a1c1?auto=format&fit=crop&w=200&q=80"
                  alt={currentSite.name}
                  className="center-node-img"
                />
              </div>
            </div>
            <span className="center-node-label">{currentSite.name}</span>
          </div>
        )}

        {/* Orbital Satellite Nodes */}
        {orbitalNodes.map((node, idx) => {
          const posStyle = satellitePositions[idx] || {};
          return (
            <div
              key={node.id}
              className={`orbital-node quadrant-${idx} ${
                node.targetSite ? "interactive" : ""
              }`}
              style={posStyle}
              onClick={() => {
                if (node.targetSite) {
                  onSelectConnectedSite(node.targetSite);
                }
              }}
              title={node.targetSite ? `Explore ${node.label}` : node.label}
            >
              <div className="orbital-node-circle">
                <img
                  src={`https://images.unsplash.com/photo-${
                    idx === 0
                      ? "1590050752117-238cb0fb12b1"
                      : idx === 1
                      ? "1548013146-72479768bada"
                      : idx === 2
                      ? "1564507592333-c60657eea523"
                      : "1600100397608-f010f44390b2"
                  }?auto=format&fit=crop&w=150&q=80`}
                  alt={node.label}
                  className="orbital-node-img"
                />
              </div>
              <span className="orbital-node-label">{node.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
export default KnowledgeGraphView;
