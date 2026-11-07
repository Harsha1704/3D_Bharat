import React, { useMemo, useRef, useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import {
  MapPin,
  ArrowRight,
  Plus,
  Minus,
  Crosshair,
  BookOpen,
} from "lucide-react";
import type { HeritageSite } from "../api";
import "leaflet/dist/leaflet.css";

interface InteractiveIndiaMapProps {
  sites: HeritageSite[];
  selectedSite: HeritageSite | null;
  onSelectSite: (site: HeritageSite) => void;
  onExploreSite: (site: HeritageSite) => void;
  onExploreAll: () => void;
}

const INDIA_CENTER: [number, number] = [22.9734, 78.6569];

// Custom Leaflet DivIcon with golden glowing aura
function createGoldenMarker(isSelected: boolean): L.DivIcon {
  return L.divIcon({
    className: "custom-map-marker-container",
    html: `
      <div class="golden-map-pin ${isSelected ? "selected" : ""}">
        <div class="pin-halo"></div>
        <div class="pin-inner">
          <svg viewBox="0 0 24 24" fill="currentColor" class="pin-icon">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
          </svg>
        </div>
      </div>
    `,
    iconSize: isSelected ? [42, 42] : [32, 32],
    iconAnchor: isSelected ? [21, 40] : [16, 30],
  });
}

// Controller to fly to site when selected
function MapFlyController({ site }: { site: HeritageSite | null }) {
  const map = useMap();
  const prevIdRef = useRef<number | null>(null);

  useEffect(() => {
    if (!site || !site.latitude || !site.longitude) return;
    if (prevIdRef.current === site.id) return;
    prevIdRef.current = site.id;

    map.flyTo([site.latitude, site.longitude], Math.max(map.getZoom(), 7), {
      duration: 1.2,
      easeLinearity: 0.25,
    });
  }, [site, map]);

  return null;
}

// Custom Zoom & Recenter controls component
function CustomMapControls({ onRecenter }: { onRecenter: () => void }) {
  const map = useMap();

  return (
    <div className="map-custom-controls">
      <button
        className="map-ctrl-btn"
        onClick={() => map.zoomIn()}
        title="Zoom In"
        aria-label="Zoom in"
      >
        <Plus className="w-4 h-4 text-amber-300" />
      </button>
      <button
        className="map-ctrl-btn"
        onClick={() => map.zoomOut()}
        title="Zoom Out"
        aria-label="Zoom out"
      >
        <Minus className="w-4 h-4 text-amber-300" />
      </button>
      <button
        className="map-ctrl-btn"
        onClick={onRecenter}
        title="Recenter India"
        aria-label="Recenter map to India"
      >
        <Crosshair className="w-4 h-4 text-amber-300" />
      </button>
    </div>
  );
}

// Representative monument fallback imagery matching golden aesthetics
const MONUMENT_THUMBNAILS: Record<string, string> = {
  default: "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=400&q=80",
  temple: "https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?auto=format&fit=crop&w=400&q=80",
  golden: "https://images.unsplash.com/photo-1588096344356-9a425330a1c1?auto=format&fit=crop&w=400&q=80",
  taj: "https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=400&q=80",
  fort: "https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=400&q=80",
  konark: "https://images.unsplash.com/photo-1600100397608-f010f44390b2?auto=format&fit=crop&w=400&q=80",
};

function getThumbnailForSite(site: HeritageSite): string {
  const name = site.name.toLowerCase();
  const cat = (site.category || "").toLowerCase();
  if (name.includes("golden") || name.includes("harmandir")) return MONUMENT_THUMBNAILS.golden;
  if (name.includes("taj")) return MONUMENT_THUMBNAILS.taj;
  if (name.includes("konark") || name.includes("sun")) return MONUMENT_THUMBNAILS.konark;
  if (cat.includes("fort")) return MONUMENT_THUMBNAILS.fort;
  if (cat.includes("temple")) return MONUMENT_THUMBNAILS.temple;
  return MONUMENT_THUMBNAILS.default;
}

export const InteractiveIndiaMap: React.FC<InteractiveIndiaMapProps> = ({
  sites,
  selectedSite,
  onSelectSite,
  onExploreSite,
  onExploreAll,
}) => {
  const mapRef = useRef<L.Map | null>(null);

  // Filter sites with valid coordinates
  const sitesWithCoords = useMemo(() => {
    return sites.filter(
      (s) =>
        typeof s.latitude === "number" &&
        typeof s.longitude === "number" &&
        !isNaN(s.latitude) &&
        !isNaN(s.longitude)
    );
  }, [sites]);

  // Active site fallback to first site or selectedSite
  const activeDisplaySite = selectedSite || sitesWithCoords[0] || null;

  const handleRecenter = () => {
    if (mapRef.current) {
      mapRef.current.flyTo(INDIA_CENTER, 5, { duration: 1 });
    }
  };

  return (
    <div className="map-panel-card">
      {/* Panel Header */}
      <div className="panel-header">
        <div className="panel-title-group">
          <MapPin className="panel-icon text-amber-400" />
          <h3 className="panel-title">Interactive India Map</h3>
        </div>
        <button className="panel-action-link" onClick={onExploreAll}>
          <span>Explore All</span>
          <ArrowRight className="w-4 h-4 ml-1 inline" />
        </button>
      </div>

      {/* Map Canvas Area */}
      <div className="map-canvas-container">
        <MapContainer
          center={INDIA_CENTER}
          zoom={5}
          minZoom={4}
          maxZoom={14}
          zoomControl={false}
          scrollWheelZoom={true}
          className="leaflet-map-element"
          ref={mapRef}
        >
          {/* Dark Basemap Tile Layer */}
          <TileLayer
            attribution='&copy; <a href="https://carto.com/">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            subdomains="abcd"
            maxZoom={19}
          />

          <MapFlyController site={selectedSite} />
          <CustomMapControls onRecenter={handleRecenter} />

          {/* Markers */}
          {sitesWithCoords.map((site) => {
            const isSelected = selectedSite?.id === site.id;
            return (
              <Marker
                key={site.id}
                position={[site.latitude!, site.longitude!]}
                icon={createGoldenMarker(isSelected)}
                eventHandlers={{
                  click: () => onSelectSite(site),
                }}
              />
            );
          })}
        </MapContainer>

        {/* Floating Selected Site Popover Card matching reference */}
        {activeDisplaySite && (
          <div className="map-site-popover-card">
            <div className="popover-img-wrapper">
              <img
                src={getThumbnailForSite(activeDisplaySite)}
                alt={activeDisplaySite.name}
                className="popover-monument-img"
                loading="lazy"
              />
              <span className="popover-category-tag">
                {activeDisplaySite.category || "Monument"}
              </span>
            </div>

            <div className="popover-content">
              <h4 className="popover-title">{activeDisplaySite.name}</h4>
              <div className="popover-location">
                <MapPin className="w-3.5 h-3.5 inline mr-1 text-amber-400" />
                <span>
                  {activeDisplaySite.city || activeDisplaySite.district || "India"}
                  {activeDisplaySite.state ? `, ${activeDisplaySite.state}` : ""}
                </span>
              </div>
              <p className="popover-desc">
                {activeDisplaySite.description
                  ? activeDisplaySite.description.slice(0, 85) + "..."
                  : "A renowned symbol of Indian cultural heritage, spiritual devotion and architectural brilliance."}
              </p>

              <button
                className="explore-site-btn"
                onClick={() => onExploreSite(activeDisplaySite)}
              >
                <span>Explore Site</span>
                <ArrowRight className="w-4 h-4 ml-1.5" />
              </button>
            </div>
          </div>
        )}

        {/* Bottom Map Status Indicators */}
        <div className="map-bottom-pills">
          <div className="status-pill live">
            <span className="pulse-indicator" />
            <span className="pill-text">Live Heritage Data</span>
          </div>

          <div className="status-pill count">
            <BookOpen className="w-3.5 h-3.5 text-amber-400 mr-1.5" />
            <span className="pill-text">
              {sites.length} Documented Sites
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
export default InteractiveIndiaMap;
