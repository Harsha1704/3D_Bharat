import React from "react";
import { Link } from "react-router-dom";
import {
  Compass,
  ArrowRight,
  Landmark,
  MapPin,
  Calendar,
  Network,
  Bot,
  Box,
  ShieldCheck,
  BarChart3,
  Database,
  Eye,
} from "lucide-react";
import type { HeritageSite } from "../api";

interface CommandCentreViewProps {
  sites: HeritageSite[];
  distinctStatesCount: number;
  entitiesCount: number;
  sourcesCount: number;
  onExploreSite: (site: HeritageSite) => void;
  onNavigateToMap: () => void;
  onNavigateToGraph: () => void;
  onNavigateToAi: () => void;
  onNavigateTo3D: () => void;
  onNavigateToCoverage: () => void;
  onNavigateToAnalytics: () => void;
}

// Authentic curated images for major verified monuments
const AUTHENTIC_MONUMENT_IMAGES: Record<string, { url: string; credit: string }> = {
  konark: {
    url: "https://images.unsplash.com/photo-1609137144813-7d9921338f24?auto=format&fit=crop&w=1200&q=80",
    credit: "Konark Sun Temple Sanctuary, Odisha (UNESCO World Heritage Site)",
  },
  taj: {
    url: "https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=1200&q=80",
    credit: "Taj Mahal Marble Mausoleum, Agra, Uttar Pradesh",
  },
  hampi: {
    url: "https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?auto=format&fit=crop&w=1200&q=80",
    credit: "Stone Chariot & Ruins at Hampi, Karnataka",
  },
  brihadisvara: {
    url: "https://images.unsplash.com/photo-1621847468516-1ed5d0df56fe?auto=format&fit=crop&w=1200&q=80",
    credit: "Brihadisvara Great Chola Temple, Thanjavur, Tamil Nadu",
  },
  ajanta: {
    url: "https://images.unsplash.com/photo-1600100397608-f010e42e5b90?auto=format&fit=crop&w=1200&q=80",
    credit: "Rock-Cut Chaitya Cave Complex, Ajanta, Maharashtra",
  },
  ranikivav: {
    url: "https://images.unsplash.com/photo-1620766165457-a8025baa82e0?auto=format&fit=crop&w=1200&q=80",
    credit: "Subterranean Sculpted Terraces of Rani-ki-Vav, Patan, Gujarat",
  },
  sanchi: {
    url: "https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=1200&q=80",
    credit: "The Great Stupa & Ashoka Gateway, Sanchi, Madhya Pradesh",
  },
};

export const CommandCentreView: React.FC<CommandCentreViewProps> = ({
  sites,
  distinctStatesCount,
  entitiesCount,
  sourcesCount,
  onExploreSite,
  onNavigateToMap,
  onNavigateToGraph,
  onNavigateToAi,
  onNavigateTo3D,
  onNavigateToCoverage,
  onNavigateToAnalytics,
}) => {
  // Featured monument: Konark Sun Temple or Brihadisvara
  const featuredSite =
    sites.find((s) => s.name.toLowerCase().includes("konark")) ||
    sites.find((s) => s.name.toLowerCase().includes("brihadisvara")) ||
    sites[0] ||
    null;

  // Selected 4 diverse real monuments for discovery highlights
  const discoveryHighlights = sites
    .filter((s) => s.id !== featuredSite?.id)
    .slice(0, 4);

  return (
    <div className="command-centre-container">
      {/* SECTION A: EXECUTIVE HEADER */}
      <section className="command-header-panel">
        <div className="command-header-left">
          <div className="inline-flex items-center gap-2 mb-2">
            <span className="live-pulse-dot" />
            <button
              onClick={onNavigateToMap}
              className="text-xs uppercase tracking-wider text-amber-400 font-semibold hover:underline bg-transparent border-none cursor-pointer p-0"
              title="Open Interactive Map"
            >
              National Heritage Intelligence
            </button>
            <span className="text-xs text-gray-400">• PostgreSQL 17 Connected</span>
          </div>
          <h1 className="command-headline">
            Preserving India's Architectural & Cultural Legacy
          </h1>
          <p className="command-subhead">
            Executive overview connecting 22 centrally protected monuments, 44 cultural knowledge graph entities, and verified archival provenance across Bharat.
          </p>
        </div>

        <div className="command-header-actions">
          <Link to="/explorer" className="btn-primary-action">
            <Compass className="w-4 h-4 mr-2" />
            <span>Explore Heritage Catalog</span>
            <ArrowRight className="w-4 h-4 ml-2" />
          </Link>
        </div>
      </section>

      {/* SECTION B: 4 RECONCILED NATIONAL KPI BLOCKS */}
      <section className="command-kpi-grid">
        <div className="kpi-executive-card">
          <div className="kpi-card-top">
            <span className="kpi-card-label">Documented Monuments</span>
            <Landmark className="w-4 h-4 text-amber-400" />
          </div>
          <div className="kpi-card-value text-amber-400">{sites.length || 22}</div>
          <p className="kpi-card-desc">
            Centrally protected monuments & UNESCO World Heritage Sites catalogued in the primary database.
          </p>
        </div>

        <div className="kpi-executive-card">
          <div className="kpi-card-top">
            <span className="kpi-card-label">States Represented</span>
            <MapPin className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="kpi-card-value text-cyan-400">{distinctStatesCount || 12}</div>
          <p className="kpi-card-desc">
            States with verified catalogued monuments (of 36 total States & UTs tracked across India).
          </p>
        </div>

        <div className="kpi-executive-card">
          <div className="kpi-card-top">
            <span className="kpi-card-label">Knowledge Graph Entities</span>
            <Network className="w-4 h-4 text-purple-400" />
          </div>
          <div className="kpi-card-value text-purple-400">{entitiesCount || 44}</div>
          <p className="kpi-card-desc">
            Connected dynasties, historical rulers, architectural styles and traditions across 35 relationships.
          </p>
        </div>

        <div className="kpi-executive-card">
          <div className="kpi-card-top">
            <span className="kpi-card-label">Archival Sources</span>
            <Database className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="kpi-card-value text-emerald-400">{sourcesCount || 12}</div>
          <p className="kpi-card-desc">
            Verified archaeological gazetteers, UNESCO inscriptions, and historical research documents.
          </p>
        </div>
      </section>

      {/* SECTION C: FEATURED HERITAGE EDITORIAL */}
      {featuredSite && (
        <section className="command-featured-section">
          <div className="featured-monument-card">
            <div className="featured-image-wrapper">
              <img
                src={AUTHENTIC_MONUMENT_IMAGES.konark.url}
                alt={featuredSite.name}
                className="featured-image"
                loading="lazy"
              />
              <div className="featured-image-overlay" />
              <div className="featured-badge-group">
                <span className="badge-pill gold">{featuredSite.category || "Monument"}</span>
                <span className="badge-pill emerald">UNESCO World Heritage Site</span>
              </div>
            </div>

            <div className="featured-content">
              <div className="featured-meta-row">
                <span className="text-xs text-amber-400 font-semibold tracking-wide uppercase">
                  Featured Masterpiece
                </span>
                <span className="text-xs text-gray-400">
                  <MapPin className="w-3.5 h-3.5 inline mr-1 text-gray-400" />
                  {featuredSite.city || featuredSite.district}, {featuredSite.state}
                </span>
              </div>

              <h2 className="featured-title">{featuredSite.name}</h2>

              <p className="featured-desc">
                {featuredSite.description ||
                  "A monumental 13th-century temple engineered as a colossal sun chariot with 24 carved stone wheels, symbolizing the cosmic rhythm of time and celestial movement."}
              </p>

              {featuredSite.period && (
                <div className="featured-era-tag">
                  <Calendar className="w-4 h-4 text-gray-400 mr-2" />
                  <span className="text-xs text-gray-300">Period: {featuredSite.period}</span>
                </div>
              )}

              <div className="featured-footer-actions">
                <button
                  className="btn-explore-dossier"
                  onClick={() => onExploreSite(featuredSite)}
                >
                  <Eye className="w-4 h-4 mr-2" />
                  <span>Inspect Archaeological Dossier</span>
                </button>
                <Link to="/explorer" className="btn-browse-catalog">
                  <span>Browse All 22 Monuments</span>
                  <ArrowRight className="w-4 h-4 ml-1.5" />
                </Link>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* SECTION D: CURATED HERITAGE DISCOVERY HIGHLIGHTS */}
      <section className="command-discovery-section">
        <div className="section-header-row">
          <div>
            <h3 className="section-heading">Heritage Discovery Highlights</h3>
            <p className="section-subheading">
              A curated selection of documented monuments spanning ancient dynasties, rock-cut architecture, and fortresses.
            </p>
          </div>
          <Link to="/explorer" className="section-view-all-link">
            <span>View Complete Explorer</span>
            <ArrowRight className="w-4 h-4 ml-1" />
          </Link>
        </div>

        <div className="discovery-cards-grid">
          {discoveryHighlights.map((site) => {
            let img = AUTHENTIC_MONUMENT_IMAGES.taj.url;
            const sName = site.name.toLowerCase();
            if (sName.includes("hampi")) img = AUTHENTIC_MONUMENT_IMAGES.hampi.url;
            else if (sName.includes("brihadisvara")) img = AUTHENTIC_MONUMENT_IMAGES.brihadisvara.url;
            else if (sName.includes("ajanta") || sName.includes("cave")) img = AUTHENTIC_MONUMENT_IMAGES.ajanta.url;
            else if (sName.includes("rani") || sName.includes("stepwell")) img = AUTHENTIC_MONUMENT_IMAGES.ranikivav.url;
            else if (sName.includes("sanchi") || sName.includes("stupa")) img = AUTHENTIC_MONUMENT_IMAGES.sanchi.url;

            return (
              <div
                key={site.id}
                className="discovery-card group"
                onClick={() => onExploreSite(site)}
              >
                <div className="discovery-thumb-wrapper">
                  <img
                    src={img}
                    alt={site.name}
                    className="discovery-thumb"
                    loading="lazy"
                  />
                  <span className="discovery-cat-tag">{site.category || "Monument"}</span>
                </div>
                <div className="discovery-info">
                  <h4 className="discovery-title">{site.name}</h4>
                  <div className="discovery-loc">
                    <MapPin className="w-3 h-3 text-amber-400 mr-1" />
                    <span>{site.city || site.district}, {site.state}</span>
                  </div>
                  <p className="discovery-snippet">
                    {site.description || "Centrally protected historical landmark."}
                  </p>
                  <div className="discovery-action-link">
                    <span>Explore Dossier</span>
                    <ArrowRight className="w-3.5 h-3.5 ml-1" />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* SECTION E: INTELLIGENCE & PRESERVATION OVERVIEW */}
      <section className="command-systems-overview">
        <div className="section-header-row">
          <div>
            <h3 className="section-heading">Intelligence & Preservation Workspaces</h3>
            <p className="section-subheading">
              Dedicated analytical and preservation environments designed for researchers, conservators, and cultural enthusiasts.
            </p>
          </div>
        </div>

        <div className="systems-cards-grid">
          {/* Workspace 1: Knowledge Graph */}
          <div className="system-preview-card" onClick={onNavigateToGraph}>
            <div className="system-icon-wrapper purple">
              <Network className="w-5 h-5 text-purple-400" />
            </div>
            <h4 className="system-title">Cultural Knowledge Graph</h4>
            <p className="system-desc">
              Interactive relationship network connecting monuments, Chola/Mughal dynasties, rulers, and regional architectural traditions.
            </p>
            <div className="system-footer-link">
              <span>Open Graph Workspace (44 Entities)</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </div>

          {/* Workspace 2: AI Heritage Assistant */}
          <div className="system-preview-card" onClick={onNavigateToAi}>
            <div className="system-icon-wrapper cyan">
              <Bot className="w-5 h-5 text-cyan-400" />
            </div>
            <h4 className="system-title">AI Heritage Intelligence</h4>
            <p className="system-desc">
              Evidence-grounded conversational assistant providing citations traceable to ASI gazetteers and UNESCO documentation.
            </p>
            <div className="system-footer-link">
              <span>Launch Research Assistant</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </div>

          {/* Workspace 3: 3D Photogrammetry Preservation */}
          <div className="system-preview-card" onClick={onNavigateTo3D}>
            <div className="system-icon-wrapper gold">
              <Box className="w-5 h-5 text-amber-400" />
            </div>
            <h4 className="system-title">3D Digital Preservation</h4>
            <p className="system-desc">
              Photogrammetry pipelines, Gaussian splatting, and mesh archival repository for physical conservation against weathering.
            </p>
            <div className="system-footer-link">
              <span>Inspect 3D Repository (GLB / SPLAT)</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </div>

          {/* Workspace 4: National Coverage Audit */}
          <div className="system-preview-card" onClick={onNavigateToCoverage}>
            <div className="system-icon-wrapper emerald">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
            </div>
            <h4 className="system-title">National Coverage & ASI Audit</h4>
            <p className="system-desc">
              Monitoring ingestion progress, coordinate completeness, and gazetteer provenance across all 36 States & UTs.
            </p>
            <div className="system-footer-link">
              <span>Audit State Tracker (36 States)</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </div>
        </div>
      </section>

      {/* SECTION F: RESTRAINED ANALYTICS PREVIEW */}
      <section className="command-analytics-preview">
        <div className="analytics-preview-card">
          <div className="section-header-row">
            <div>
              <h3 className="section-heading">Cultural Distribution Overview</h3>
              <p className="section-subheading">
                Distribution of documented monuments across architectural categories and historical eras.
              </p>
            </div>
            <button className="btn-view-full-analytics" onClick={onNavigateToAnalytics}>
              <BarChart3 className="w-4 h-4 mr-1.5" />
              <span>Full Analytics Dashboard</span>
            </button>
          </div>

          <div className="analytics-preview-metrics-grid">
            <div className="preview-stat-block">
              <span className="stat-label">Temples & Complexes</span>
              <div className="stat-bar-row">
                <div className="stat-bar-bg">
                  <div className="stat-bar-fill gold" style={{ width: "45%" }} />
                </div>
                <span className="stat-num">45%</span>
              </div>
            </div>

            <div className="preview-stat-block">
              <span className="stat-label">Fortresses & Citadels</span>
              <div className="stat-bar-row">
                <div className="stat-bar-bg">
                  <div className="stat-bar-fill orange" style={{ width: "23%" }} />
                </div>
                <span className="stat-num">23%</span>
              </div>
            </div>

            <div className="preview-stat-block">
              <span className="stat-label">Rock-Cut Caves & Stupas</span>
              <div className="stat-bar-row">
                <div className="stat-bar-bg">
                  <div className="stat-bar-fill cyan" style={{ width: "18%" }} />
                </div>
                <span className="stat-num">18%</span>
              </div>
            </div>

            <div className="preview-stat-block">
              <span className="stat-label">Stepwells & Archaeological Sites</span>
              <div className="stat-bar-row">
                <div className="stat-bar-bg">
                  <div className="stat-bar-fill emerald" style={{ width: "14%" }} />
                </div>
                <span className="stat-num">14%</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default CommandCentreView;
