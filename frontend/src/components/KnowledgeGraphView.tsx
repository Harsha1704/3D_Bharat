import React, { useMemo } from "react";
import { Network, ArrowRight, Link2, Landmark } from "lucide-react";
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
  relationshipType: string;
  category: "documented" | "architectural" | "regional";
  targetSite?: HeritageSite;
}

export const KnowledgeGraphView: React.FC<KnowledgeGraphViewProps> = ({
  selectedSite,
  allSites,
  connections,
  onSelectConnectedSite,
  onViewFullGraph,
}) => {
  const currentSite = selectedSite || allSites[0] || null;

  // Build authentic orbital nodes derived strictly from database records
  const orbitalNodes = useMemo<OrbitalNode[]>(() => {
    if (!currentSite) return [];

    const nodes: OrbitalNode[] = [];
    const seenSiteIds = new Set<number>([currentSite.id]);

    // 1. Direct documented connections from database
    const directConnections = connections.filter(
      (c) =>
        c.source_site_id === currentSite.id || c.target_site_id === currentSite.id
    );

    for (const conn of directConnections) {
      const otherId =
        conn.source_site_id === currentSite.id
          ? conn.target_site_id
          : conn.source_site_id;

      if (!seenSiteIds.has(otherId)) {
        seenSiteIds.add(otherId);
        const otherSite = allSites.find((s) => s.id === otherId);
        if (otherSite) {
          nodes.push({
            id: otherSite.id,
            label: otherSite.name,
            relationshipType: conn.relationship_type.replace(/_/g, " "),
            category: "documented",
            targetSite: otherSite,
          });
        }
      }
    }

    // 2. Architectural peers (same category in DB)
    if (currentSite.category) {
      const categoryPeers = allSites.filter(
        (s) =>
          !seenSiteIds.has(s.id) &&
          s.category &&
          s.category.toLowerCase() === currentSite.category!.toLowerCase()
      );

      for (const peer of categoryPeers.slice(0, 2)) {
        seenSiteIds.add(peer.id);
        nodes.push({
          id: peer.id,
          label: peer.name,
          relationshipType: `Shared ${currentSite.category} Style`,
          category: "architectural",
          targetSite: peer,
        });
      }
    }

    // 3. Regional peers (same state in DB)
    if (nodes.length < 4 && currentSite.state) {
      const statePeers = allSites.filter(
        (s) =>
          !seenSiteIds.has(s.id) &&
          s.state &&
          s.state.toLowerCase() === currentSite.state!.toLowerCase()
      );

      for (const peer of statePeers.slice(0, 1)) {
        seenSiteIds.add(peer.id);
        nodes.push({
          id: peer.id,
          label: peer.name,
          relationshipType: `${currentSite.state} Heritage`,
          category: "regional",
          targetSite: peer,
        });
      }
    }

    return nodes.slice(0, 4);
  }, [currentSite, connections, allSites]);

  // Satellite node polar positions
  const satellitePositions = [
    { top: "14%", left: "14%" },
    { top: "14%", right: "14%" },
    { bottom: "14%", right: "14%" },
    { bottom: "14%", left: "14%" },
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
        {orbitalNodes.length > 0 ? (
          <>
            {/* SVG Connecting Light Rays */}
            <svg
              className="radial-beams-svg"
              viewBox="0 0 100 100"
              preserveAspectRatio="none"
            >
              {orbitalNodes.map((_, idx) => {
                const targetPoints = [
                  { x: 22, y: 22 },
                  { x: 78, y: 22 },
                  { x: 78, y: 78 },
                  { x: 22, y: 78 },
                ];
                const pt = targetPoints[idx];
                return (
                  <line
                    key={idx}
                    x1="50"
                    y1="50"
                    x2={pt.x}
                    y2={pt.y}
                    stroke="url(#beamGrad)"
                    strokeWidth="1.5"
                    strokeDasharray="3 2"
                  />
                );
              })}

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
                    <Landmark className="w-7 h-7 text-amber-300" />
                  </div>
                </div>
                <span className="center-node-label">{currentSite.name}</span>
                <span className="center-node-type">Focus Monument</span>
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
                  title={
                    node.targetSite
                      ? `Inspect relationship: ${node.relationshipType}`
                      : node.label
                  }
                >
                  <div className="orbital-node-circle">
                    <Link2 className="w-4 h-4 text-amber-400" />
                  </div>
                  <span className="orbital-node-label">{node.label}</span>
                  <span className="orbital-node-rel-badge">
                    {node.relationshipType}
                  </span>
                </div>
              );
            })}
          </>
        ) : (
          <div className="graph-empty-state">
            <Network className="w-8 h-8 text-amber-400/60 mb-2" />
            <h5 className="text-white font-semibold text-sm">
              No Documented Connections
            </h5>
            <p className="text-xs text-gray-400 max-w-xs text-center mt-1">
              {currentSite?.name} currently has no recorded direct connections in
              the verified 8-connection national baseline.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
export default KnowledgeGraphView;
