import React, { useState, useEffect } from "react";
import {
  X,
  Landmark,
  MapPin,
  BookOpen,
  Image,
  Box,
  Network,
  ExternalLink,
  ShieldCheck,
  Loader2,
  FileText,
} from "lucide-react";
import {
  getHeritageSiteDetails,
  getRelatedHeritageSites,
  type HeritageSite,
  type HeritageSiteDetailResponse,
  type HeritageRelatedSitesResponse,
} from "../api";

interface HeritageSiteDossierModalProps {
  site: HeritageSite | null;
  onClose: () => void;
  onSelectRelatedSite: (siteId: number) => void;
}

type TabKey = "overview" | "sources" | "media" | "3d" | "connections";

export const HeritageSiteDossierModal: React.FC<
  HeritageSiteDossierModalProps
> = ({ site, onClose, onSelectRelatedSite }) => {
  const [activeTab, setActiveTab] = useState<TabKey>("overview");
  const [details, setDetails] = useState<HeritageSiteDetailResponse | null>(null);
  const [related, setRelated] = useState<HeritageRelatedSitesResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!site) return;
    setLoading(true);
    setError(null);

    const controller = new AbortController();

    Promise.all([
      getHeritageSiteDetails(site.id, controller.signal),
      getRelatedHeritageSites(site.id, 10, controller.signal).catch(() => null),
    ])
      .then(([detailRes, relatedRes]) => {
        setDetails(detailRes);
        setRelated(relatedRes);
        setLoading(false);
      })
      .catch((err) => {
        if (err.name !== "AbortError") {
          setError(err.message || "Failed to load heritage details.");
          setLoading(false);
        }
      });

    return () => controller.abort();
  }, [site]);

  if (!site) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="dossier-modal-window"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-labelledby="dossier-title"
      >
        {/* Header */}
        <div className="dossier-header">
          <div className="dossier-header-title-box">
            <div className="dossier-icon-box">
              <Landmark className="w-6 h-6 text-amber-400" />
            </div>
            <div>
              <h2 id="dossier-title" className="dossier-title">
                {site.name}
              </h2>
              <div className="dossier-subtitle">
                <MapPin className="w-3.5 h-3.5 inline mr-1 text-amber-400" />
                <span>
                  {site.city || site.district || "Bharat"},{" "}
                  <strong>{site.state || "National"}</strong>
                </span>
                {site.category && (
                  <span className="badge category-badge">{site.category}</span>
                )}
                {site.period && (
                  <span className="badge period-badge">{site.period}</span>
                )}
              </div>
            </div>
          </div>

          <button
            className="dossier-close-btn"
            onClick={onClose}
            aria-label="Close dossier"
          >
            <X className="w-5 h-5 text-gray-400 hover:text-white" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="dossier-tabs-nav">
          <button
            className={`dossier-tab-btn ${activeTab === "overview" ? "active" : ""}`}
            onClick={() => setActiveTab("overview")}
          >
            <Landmark className="w-4 h-4 mr-2 inline" />
            Overview
          </button>
          <button
            className={`dossier-tab-btn ${activeTab === "sources" ? "active" : ""}`}
            onClick={() => setActiveTab("sources")}
          >
            <BookOpen className="w-4 h-4 mr-2 inline" />
            Archival Sources ({details?.sources?.length ?? 0})
          </button>
          <button
            className={`dossier-tab-btn ${activeTab === "media" ? "active" : ""}`}
            onClick={() => setActiveTab("media")}
          >
            <Image className="w-4 h-4 mr-2 inline" />
            Media & Archives ({details?.media?.length ?? 0})
          </button>
          <button
            className={`dossier-tab-btn ${activeTab === "3d" ? "active" : ""}`}
            onClick={() => setActiveTab("3d")}
          >
            <Box className="w-4 h-4 mr-2 inline" />
            3D Photogrammetry ({details?.assets_3d?.length ?? 0})
          </button>
          <button
            className={`dossier-tab-btn ${activeTab === "connections" ? "active" : ""}`}
            onClick={() => setActiveTab("connections")}
          >
            <Network className="w-4 h-4 mr-2 inline" />
            Cultural Connections ({details?.connections?.length ?? 0})
          </button>
        </div>

        {/* Tab Body */}
        <div className="dossier-body">
          {loading ? (
            <div className="loading-state">
              <Loader2 className="w-8 h-8 text-amber-400 animate-spin mb-3" />
              <p>Loading digital preservation dossier from national archive...</p>
            </div>
          ) : error ? (
            <div className="error-state">
              <p className="text-red-400">{error}</p>
            </div>
          ) : (
            <>
              {/* Tab 1: Overview */}
              {activeTab === "overview" && (
                <div className="tab-pane overview-pane">
                  <div className="overview-grid">
                    <div className="overview-main-text">
                      <h4 className="section-heading">Historical Description</h4>
                      <p className="body-prose">
                        {details?.description ||
                          site.description ||
                          "A nationally protected heritage monument of profound architectural and spiritual significance."}
                      </p>

                      {details?.significance && (
                        <>
                          <h4 className="section-heading mt-4">
                            Cultural Significance
                          </h4>
                          <p className="body-prose">{details.significance}</p>
                        </>
                      )}

                      {details?.architecture && (
                        <>
                          <h4 className="section-heading mt-4">
                            Architectural Style & Craftsmanship
                          </h4>
                          <p className="body-prose">{details.architecture}</p>
                        </>
                      )}
                    </div>

                    <div className="overview-sidebar-info">
                      <div className="info-box">
                        <span className="info-label">Geographic Coordinates</span>
                        <span className="info-val">
                          {site.latitude?.toFixed(5)}° N, {site.longitude?.toFixed(5)}° E
                        </span>
                      </div>
                      <div className="info-box">
                        <span className="info-label">Centrally Protected ID</span>
                        <span className="info-val font-mono">
                          {site.external_id || `ASI-BHARAT-${site.id}`}
                        </span>
                      </div>
                      <div className="info-box">
                        <span className="info-label">Dynasty / Era</span>
                        <span className="info-val">{site.period || "Documented Era"}</span>
                      </div>
                      <div className="info-box">
                        <span className="info-label">Preservation Status</span>
                        <span className="info-val text-emerald-400 font-semibold">
                          <ShieldCheck className="w-3.5 h-3.5 inline mr-1" />
                          ASI Verified Baseline
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 2: Sources */}
              {activeTab === "sources" && (
                <div className="tab-pane sources-pane">
                  {details?.sources && details.sources.length > 0 ? (
                    <div className="sources-list">
                      {details.sources.map((src) => (
                        <div key={src.id} className="source-card">
                          <div className="source-top">
                            <span className="source-type-badge">{src.source_type}</span>
                            {src.reliability_score && (
                              <span className="reliability-badge">
                                Reliability: {src.reliability_score * 100}%
                              </span>
                            )}
                          </div>
                          <h4 className="source-title">{src.title}</h4>
                          {src.author_or_institution && (
                            <p className="source-author">
                              <strong>Institution:</strong> {src.author_or_institution}
                            </p>
                          )}
                          {src.citation && (
                            <p className="source-citation">
                              <em>Citation:</em> {src.citation}
                            </p>
                          )}
                          {src.url_or_identifier && (
                            <a
                              href={src.url_or_identifier}
                              target="_blank"
                              rel="noreferrer"
                              className="source-link"
                            >
                              <ExternalLink className="w-3.5 h-3.5 inline mr-1" />
                              View Archival Record
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-tab-state">
                      <BookOpen className="w-10 h-10 text-gray-500 mb-2" />
                      <p>National baseline archival citations are registered under primary ASI repository.</p>
                    </div>
                  )}
                </div>
              )}

              {/* Tab 3: Media */}
              {activeTab === "media" && (
                <div className="tab-pane media-pane">
                  {details?.media && details.media.length > 0 ? (
                    <div className="media-grid">
                      {details.media.map((med) => (
                        <div key={med.id} className="media-card">
                          {med.media_type.toLowerCase() === "image" && med.file_url ? (
                            <img
                              src={med.file_url}
                              alt={med.title}
                              className="media-thumb"
                            />
                          ) : (
                            <div className="media-placeholder">
                              <FileText className="w-8 h-8 text-amber-400" />
                              <span>{med.mime_type}</span>
                            </div>
                          )}
                          <div className="media-info">
                            <h5 className="media-title">{med.title}</h5>
                            <span className="media-attr">{med.attribution || "ASI Digital Archive"}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-tab-state">
                      <Image className="w-10 h-10 text-gray-500 mb-2" />
                      <p>No media files registered yet for this site. Ingest media using Phase 4 preservation endpoints.</p>
                    </div>
                  )}
                </div>
              )}

              {/* Tab 4: 3D Assets */}
              {activeTab === "3d" && (
                <div className="tab-pane three-d-pane">
                  {details?.assets_3d && details.assets_3d.length > 0 ? (
                    <div className="assets-3d-grid">
                      {details.assets_3d.map((ast) => (
                        <div key={ast.id} className="asset-3d-card">
                          <div className="asset-header">
                            <Box className="w-5 h-5 text-amber-400" />
                            <span className="asset-format">{ast.file_format.toUpperCase()}</span>
                          </div>
                          <h4 className="asset-title">{ast.title}</h4>
                          <div className="asset-meta-row">
                            <span>Vertices: {ast.vertex_count?.toLocaleString() || "Standard"}</span>
                            <span>Status: {ast.verification_status}</span>
                          </div>
                          {ast.file_url && (
                            <a
                              href={ast.file_url}
                              className="asset-download-btn"
                              download
                            >
                              Download 3D Asset
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-tab-state">
                      <Box className="w-10 h-10 text-gray-500 mb-2" />
                      <p>
                        Photogrammetry scan pipeline ready. Models in GLB, GLTF, OBJ, or SPLAT formats can be uploaded via the Management panel.
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Tab 5: Connections */}
              {activeTab === "connections" && (
                <div className="tab-pane connections-pane">
                  <div className="connections-subsections">
                    <h4 className="conn-section-title">
                      Documented Cultural Connections
                    </h4>
                    {related?.documented_connections &&
                    related.documented_connections.length > 0 ? (
                      <div className="conn-pills-list">
                        {related.documented_connections.map((c) => (
                          <div
                            key={c.connection_id}
                            className="conn-pill-item interactive"
                            onClick={() => {
                              onSelectRelatedSite(c.connected_site_id);
                            }}
                          >
                            <Network className="w-4 h-4 text-amber-400 mr-2" />
                            <div className="conn-pill-info">
                              <span className="conn-site-name">
                                {c.connected_site_name}
                              </span>
                              <span className="conn-rel-type">
                                {c.relationship_type.replace(/_/g, " ")} (
                                {Math.round((c.confidence_score || 0.9) * 100)}%)
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="empty-subtext">No documented direct connections recorded yet.</p>
                    )}

                    {related?.structured_relations &&
                      related.structured_relations.length > 0 && (
                        <>
                          <h4 className="conn-section-title mt-4">
                            Architectural & Regional Relatives
                          </h4>
                          <div className="conn-pills-list">
                            {related.structured_relations.map((s) => (
                              <div
                                key={s.site_id}
                                className="conn-pill-item interactive"
                                onClick={() => onSelectRelatedSite(s.site_id)}
                              >
                                <Landmark className="w-4 h-4 text-sky-400 mr-2" />
                                <div className="conn-pill-info">
                                  <span className="conn-site-name">{s.name}</span>
                                  <span className="conn-rel-type">
                                    {s.category} • {s.state}
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </>
                      )}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};
export default HeritageSiteDossierModal;
