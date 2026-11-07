import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMap,
} from "react-leaflet";
import { useEffect, useMemo, useState, useRef } from "react";
import L from "leaflet";
import {
  MapPin,
  Network,
  ArrowRight,
  Filter,
  Sparkles,
  Layers,
  RotateCcw,
} from "lucide-react";

import type { HeritageSite } from "../api";
import "leaflet/dist/leaflet.css";
import "./HeritageMap.css";

/* =========================================================
   TYPES
========================================================= */

interface HeritageMapProps {
  sites: HeritageSite[];
  selectedSite: HeritageSite | null;
  onSelectSite: (site: HeritageSite) => void;
  onExploreSite?: (site: HeritageSite) => void;
}

type SiteWithCoordinates = HeritageSite & {
  latitude?: number | null;
  longitude?: number | null;
  lat?: number | null;
  lng?: number | null;
};

type CategoryTheme = {
  key: string;
  label: string;
  glyph: string;
  color: string;
  glow: string;
};

/* =========================================================
   CATEGORY THEMES (BASED ON REAL SITE CATEGORIES)
========================================================= */

const CATEGORY_THEMES: Record<string, CategoryTheme> = {
  temple: {
    key: "temple",
    label: "Temple",
    glyph: "🛕",
    color: "#e5ad55", // Gold
    glow: "rgba(229, 173, 85, 0.45)",
  },
  cave: {
    key: "cave",
    label: "Rock-cut Cave",
    glyph: "⛰",
    color: "#4ecdc4", // Turquoise / Mineral
    glow: "rgba(78, 205, 196, 0.45)",
  },
  fort: {
    key: "fort",
    label: "Fort & Citadel",
    glyph: "🛡",
    color: "#e76f51", // Terracotta / Crimson
    glow: "rgba(231, 111, 81, 0.45)",
  },
  monument: {
    key: "monument",
    label: "Monument",
    glyph: "🏛",
    color: "#f4a261", // Sandstone / Amber
    glow: "rgba(244, 162, 97, 0.45)",
  },
  stupa: {
    key: "stupa",
    label: "Stupa",
    glyph: "☸",
    color: "#f1c40f", // Saffron / Brass
    glow: "rgba(241, 196, 15, 0.45)",
  },
  default: {
    key: "default",
    label: "Heritage",
    glyph: "✦",
    color: "#e5ad55",
    glow: "rgba(229, 173, 85, 0.4)",
  },
};

function getCategoryTheme(category?: string | null): CategoryTheme {
  if (!category) return CATEGORY_THEMES.default;
  const c = category.toLowerCase();
  if (c.includes("temple")) return CATEGORY_THEMES.temple;
  if (c.includes("cave") || c.includes("rock-cut")) return CATEGORY_THEMES.cave;
  if (c.includes("fort") || c.includes("citadel") || c.includes("fortress"))
    return CATEGORY_THEMES.fort;
  if (c.includes("stupa")) return CATEGORY_THEMES.stupa;
  if (c.includes("monument") || c.includes("mausoleum"))
    return CATEGORY_THEMES.monument;
  return CATEGORY_THEMES.default;
}

/* =========================================================
   GEOGRAPHICAL CONSTANTS (INDIA-FOCUSED)
========================================================= */

const INDIA_CENTER: [number, number] = [22.9734, 78.6569];

const INDIA_BOUNDS: [[number, number], [number, number]] = [
  [6.0, 68.0], // South-West
  [37.5, 97.5], // North-East
];

/* =========================================================
   CUSTOM MARKER FACTORY
========================================================= */

const markerIconCache = new Map<string, L.DivIcon>();

function createCustomMarkerIcon(
  categoryTheme: CategoryTheme,
  isSelected: boolean
): L.DivIcon {
  const cacheKey = `${categoryTheme.key}-${isSelected}`;
  const cached = markerIconCache.get(cacheKey);
  if (cached) return cached;

  const icon = L.divIcon({
    className: "heritage-marker-wrapper",
    html: `
      <div class="heritage-marker ${isSelected ? "selected" : ""}" style="--cat-color: ${categoryTheme.color}; --cat-glow: ${categoryTheme.glow}">
        <div class="heritage-marker-halo"></div>
        <div class="heritage-marker-inner">
          <span class="heritage-marker-glyph">${categoryTheme.glyph}</span>
        </div>
      </div>
    `,
    iconSize: isSelected ? [48, 48] : [40, 40],
    iconAnchor: isSelected ? [24, 48] : [20, 40],
    popupAnchor: [0, isSelected ? -46 : -38],
  });

  markerIconCache.set(cacheKey, icon);
  return icon;
}

/* =========================================================
   MAP CONTROLLER (SMOOTH PAN / FLY)
========================================================= */

function MapController({
  selectedSite,
}: {
  selectedSite: HeritageSite | null;
}) {
  const map = useMap();
  const lastAnimatedIdRef = useRef<number | null>(null);

  useEffect(() => {
    if (!selectedSite) return;
    if (lastAnimatedIdRef.current === selectedSite.id) return;

    const coordinates = getCoordinates(selectedSite);
    if (!coordinates) return;

    lastAnimatedIdRef.current = selectedSite.id;
    map.flyTo(coordinates, Math.max(map.getZoom(), 8), {
      duration: 1.2,
      easeLinearity: 0.25,
    });
  }, [selectedSite, map]);

  return null;
}

/* =========================================================
   COORDINATES & LOCATION HELPERS
========================================================= */

function getCoordinates(site: HeritageSite): [number, number] | null {
  const item = site as SiteWithCoordinates;
  const latitude = item.latitude ?? item.lat;
  const longitude = item.longitude ?? item.lng;

  if (
    typeof latitude !== "number" ||
    typeof longitude !== "number" ||
    !Number.isFinite(latitude) ||
    !Number.isFinite(longitude)
  ) {
    return null;
  }

  if (
    latitude < -90 ||
    latitude > 90 ||
    longitude < -180 ||
    longitude > 180
  ) {
    return null;
  }

  return [latitude, longitude];
}

function getLocation(site: HeritageSite): string {
  const city = site.city || site.district || "";
  const state = site.state || "";

  if (city && state) return `${city}, ${state}`;
  return city || state || "Bharat";
}

/* =========================================================
   MAIN HERITAGE MAP COMPONENT
========================================================= */

export default function HeritageMap({
  sites,
  selectedSite,
  onSelectSite,
  onExploreSite,
}: HeritageMapProps) {
  const [activeCategoryFilter, setActiveCategoryFilter] = useState<string>("ALL");

  /* -------------------------------------------------------
     1. Deduplicate & Parse Coordinates safely
  ------------------------------------------------------- */
  const mappedSites = useMemo(() => {
    const seenIds = new Set<number>();
    const valid: {
      site: HeritageSite;
      coordinates: [number, number];
      categoryTheme: CategoryTheme;
    }[] = [];

    for (const site of sites) {
      if (!site || seenIds.has(site.id)) continue;
      seenIds.add(site.id);

      const coordinates = getCoordinates(site);
      if (!coordinates) continue;

      const categoryTheme = getCategoryTheme(site.category);
      valid.push({
        site,
        coordinates,
        categoryTheme,
      });
    }

    return valid;
  }, [sites]);

  /* -------------------------------------------------------
     2. Available Categories for Filter Bar
  ------------------------------------------------------- */
  const availableCategories = useMemo(() => {
    const cats = new Set<string>();
    for (const item of mappedSites) {
      cats.add(item.categoryTheme.key);
    }
    return Array.from(cats);
  }, [mappedSites]);

  /* -------------------------------------------------------
     3. Apply Interactive Category Filter
  ------------------------------------------------------- */
  const visibleSites = useMemo(() => {
    if (activeCategoryFilter === "ALL") return mappedSites;
    return mappedSites.filter(
      (item) => item.categoryTheme.key === activeCategoryFilter
    );
  }, [mappedSites, activeCategoryFilter]);

  function handleExplore(site: HeritageSite) {
    if (onExploreSite) {
      onExploreSite(site);
    } else {
      onSelectSite(site);
    }
  }

  return (
    <section className="heritage-map-section" id="heritage-map">
      {/* HEADER */}
      <div className="heritage-map-header">
        <div className="heritage-map-heading">
          <div className="section-label">GEOGRAPHIC CULTURAL NETWORK</div>
          <h2>
            Heritage across
            <br />
            <span>Bharat.</span>
          </h2>
          <p>
            Explore India's monuments and living heritage geographically.
            Select a site to view its cultural context and relationships.
          </p>
        </div>

        {/* LIVE STAT */}
        <div className="map-stat-wrapper">
          <div className="map-stat">
            <strong>{visibleSites.length}</strong>
            <span>{activeCategoryFilter === "ALL" ? "Mapped Sites" : "Filtered Sites"}</span>
          </div>
        </div>
      </div>

      {/* FILTER TOOLBAR */}
      {availableCategories.length > 1 && (
        <div className="map-filter-bar">
          <div className="filter-label">
            <Filter size={13} />
            <span>Category Filter:</span>
          </div>

          <div className="filter-chips">
            <button
              type="button"
              className={`filter-chip ${activeCategoryFilter === "ALL" ? "active" : ""}`}
              onClick={() => setActiveCategoryFilter("ALL")}
            >
              <Layers size={13} />
              <span>All ({mappedSites.length})</span>
            </button>

            {availableCategories.map((catKey) => {
              const theme = CATEGORY_THEMES[catKey] || CATEGORY_THEMES.default;
              const count = mappedSites.filter((s) => s.categoryTheme.key === catKey).length;
              return (
                <button
                  key={catKey}
                  type="button"
                  className={`filter-chip ${activeCategoryFilter === catKey ? "active" : ""}`}
                  style={{
                    borderColor:
                      activeCategoryFilter === catKey ? theme.color : undefined,
                  }}
                  onClick={() => setActiveCategoryFilter(catKey)}
                >
                  <span>{theme.glyph}</span>
                  <span>
                    {theme.label} ({count})
                  </span>
                </button>
              );
            })}

            {activeCategoryFilter !== "ALL" && (
              <button
                type="button"
                className="filter-chip reset"
                onClick={() => setActiveCategoryFilter("ALL")}
                title="Reset filters"
              >
                <RotateCcw size={13} />
                <span>Reset</span>
              </button>
            )}
          </div>
        </div>
      )}

      {/* MAP CONTAINER */}
      <div className="heritage-map-container">
        <MapContainer
          center={INDIA_CENTER}
          zoom={5}
          minZoom={4}
          maxZoom={12}
          maxBounds={INDIA_BOUNDS}
          maxBoundsViscosity={0.9}
          scrollWheelZoom={true}
          className="heritage-map"
        >
          {/* OPENSTREETMAP DARK TILES */}
          <TileLayer
            attribution='&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            subdomains="abcd"
            maxZoom={19}
          />

          {/* DYNAMIC MAP POSITION CONTROLLER */}
          <MapController selectedSite={selectedSite} />

          {/* HERITAGE MARKERS */}
          {visibleSites.map(({ site, coordinates, categoryTheme }) => {
            const isSelected = selectedSite?.id === site.id;

            return (
              <Marker
                key={site.id}
                position={coordinates}
                icon={createCustomMarkerIcon(categoryTheme, isSelected)}
                zIndexOffset={isSelected ? 1000 : 100}
                eventHandlers={{
                  click: () => onSelectSite(site),
                }}
              >
                {/* INTERACTIVE HERITAGE POPUP */}
                <Popup
                  autoPan={true}
                  autoPanPadding={[50, 50]}
                  closeButton={true}
                  className="heritage-leaflet-popup"
                >
                  <div className="heritage-popup">
                    {/* CATEGORY & PERIOD HEADER */}
                    <div className="popup-top">
                      <span
                        className="popup-category"
                        style={{ color: categoryTheme.color }}
                      >
                        {categoryTheme.glyph} {site.category || "HERITAGE"}
                      </span>
                      {site.period && (
                        <span className="popup-period">{site.period}</span>
                      )}
                    </div>

                    {/* NAME */}
                    <h3 className="popup-title">{site.name}</h3>

                    {/* LOCATION */}
                    <div className="popup-location">
                      <MapPin size={13} />
                      <span>{getLocation(site)}</span>
                    </div>

                    {/* DESCRIPTION */}
                    {site.description && (
                      <p className="popup-description">
                        {site.description}
                      </p>
                    )}

                    {/* TAGS */}
                    {site.tags && site.tags.length > 0 && (
                      <div className="popup-tags">
                        {site.tags.slice(0, 3).map((tag, idx) => (
                          <span key={idx} className="popup-tag">
                            #{tag}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* ACTIONS */}
                    <div className="popup-actions">
                      <button
                        type="button"
                        className="popup-explore-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleExplore(site);
                        }}
                      >
                        <span>Explore Site Details</span>
                        <ArrowRight size={14} />
                      </button>
                    </div>
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>

        {/* MAP OVERLAY BADGE */}
        <div className="map-overlay">
          <div className="map-live">
            <span className="live-dot" />
            <span>LIVE HERITAGE NETWORK</span>
          </div>
          <div className="map-overlay-title">3D BHARAT</div>
          <div className="map-overlay-subtitle">
            Geographic Heritage Exploration
          </div>
        </div>

        {/* MAP LEGEND */}
        <div className="map-legend">
          <div className="legend-item">
            <span className="legend-dot-selected" />
            <span>Selected Site</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot-gold" />
            <span>Temple / Shrine</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot-cave" />
            <span>Rock-cut Caves</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot-fort" />
            <span>Fort & Citadel</span>
          </div>
          <div className="legend-item">
            <Network size={13} />
            <span>Click marker for details</span>
          </div>
        </div>
      </div>

      {/* WARNING / EMPTY STATES */}
      {sites.length > 0 && mappedSites.length === 0 && (
        <div className="map-warning">
          <MapPin size={20} />
          <div>
            <strong>Geographic coordinates unavailable</strong>
            <span>
              Heritage records loaded successfully, but coordinates are missing for these items.
            </span>
          </div>
        </div>
      )}

      {sites.length === 0 && (
        <div className="map-warning empty">
          <Sparkles size={20} />
          <div>
            <strong>No heritage sites available</strong>
            <span>
              Heritage locations will appear here as soon as they are loaded from the database.
            </span>
          </div>
        </div>
      )}
    </section>
  );
}
