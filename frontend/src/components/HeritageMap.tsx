import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMap,
} from "react-leaflet";

import { useEffect, useMemo } from "react";

import L from "leaflet";

import {
  MapPin,
  Network,
  ArrowRight,
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
}

type SiteWithCoordinates = HeritageSite & {
  latitude?: number | null;
  longitude?: number | null;

  lat?: number | null;
  lng?: number | null;

  city?: string | null;
  district?: string | null;
  state?: string | null;

  category?: string | null;
  description?: string | null;
};

/* =========================================================
   INDIA DEFAULT CENTER
========================================================= */

const INDIA_CENTER: [number, number] = [
  22.9734,
  78.6569,
];

/* =========================================================
   INDIA MAP BOUNDS
========================================================= */

const INDIA_BOUNDS: [
  [number, number],
  [number, number]
] = [
  [6.0, 68.0],
  [37.5, 97.5],
];

/* =========================================================
   CUSTOM MARKER
========================================================= */

const createMarkerIcon = (
  selected = false
) =>
  L.divIcon({
    className: "heritage-marker-wrapper",

    html: `
      <div class="heritage-marker ${
        selected ? "selected" : ""
      }">

        <div class="heritage-marker-inner">
          <span>✦</span>
        </div>

      </div>
    `,

    iconSize: [42, 42],

    iconAnchor: [21, 42],

    popupAnchor: [0, -40],
  });

/* =========================================================
   MAP CONTROLLER
========================================================= */

function MapController({
  selectedSite,
}: {
  selectedSite: HeritageSite | null;
}) {
  const map = useMap();

  useEffect(() => {
    if (!selectedSite) {
      return;
    }

    const coordinates =
      getCoordinates(selectedSite);

    if (!coordinates) {
      return;
    }

    map.flyTo(
      coordinates,
      8,
      {
        duration: 1.2,
      }
    );
  }, [selectedSite, map]);

  return null;
}


/* =========================================================
   GET COORDINATES
========================================================= */

function getCoordinates(
  site: HeritageSite
): [number, number] | null {
  const item =
    site as SiteWithCoordinates;

  const latitude =
    item.latitude ?? item.lat;

  const longitude =
    item.longitude ?? item.lng;

  if (
    typeof latitude !== "number" ||
    typeof longitude !== "number"
  ) {
    return null;
  }

  if (
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

  return [
    latitude,
    longitude,
  ];
}

/* =========================================================
   LOCATION
========================================================= */

function getLocation(
  site: HeritageSite
): string {
  const item =
    site as SiteWithCoordinates;

  const city =
    item.city ||
    item.district ||
    "";

  const state =
    item.state ||
    "";

  if (
    city &&
    state
  ) {
    return `${city}, ${state}`;
  }

  return (
    city ||
    state ||
    "India"
  );
}

/* =========================================================
   MAP COMPONENT
========================================================= */

export default function HeritageMap({
  sites,
  selectedSite,
  onSelectSite,
}: HeritageMapProps) {

  /* =======================================================
     MAP SITES
  ======================================================= */

  const mappedSites =
    useMemo(() => {

      return sites

        .map((site) => ({
          site,

          coordinates:
            getCoordinates(site),
        }))

        .filter(
          (
            item
          ): item is {
            site: HeritageSite;

            coordinates: [
              number,
              number
            ];
          } =>
            item.coordinates !== null
        );

    }, [sites]);

  /* =======================================================
     RENDER
  ======================================================= */

  return (
    <section
      className="heritage-map-section"
      id="heritage-map"
    >

      {/* =================================================
          HEADER
      ================================================= */}

      <div className="heritage-map-header">

        <div className="heritage-map-heading">

          <div className="section-label">
            GEOGRAPHIC CULTURAL NETWORK
          </div>

          <h2>
            Heritage across
            <br />
            <span>Bharat.</span>
          </h2>

          <p>
            Explore heritage sites geographically
            and discover the cultural relationships
            connecting India's diverse regions.
          </p>

        </div>

        {/* =================================================
            LIVE COUNTER
        ================================================= */}

        <div className="map-stat">

          <strong>
            {mappedSites.length}
          </strong>

          <span>
            Mapped Sites
          </span>

        </div>

      </div>

      {/* =================================================
          MAP CONTAINER
      ================================================= */}

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

          {/* =================================================
              OPENSTREETMAP
          ================================================= */}

          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* =================================================
              SELECTED SITE CONTROLLER
          ================================================= */}

          <MapController
            selectedSite={selectedSite}
          />

          {/* =================================================
              HERITAGE MARKERS
          ================================================= */}

          {mappedSites.map(
            ({
              site,
              coordinates,
            }) => {

              const isSelected =
                selectedSite?.id ===
                site.id;

              const item =
                site as SiteWithCoordinates;

              return (
                <Marker
                  key={site.id}

                  position={
                    coordinates
                  }

                  icon={
                    createMarkerIcon(
                      isSelected
                    )
                  }

                  eventHandlers={{
                    click: () =>
                      onSelectSite(
                        site
                      ),
                  }}
                >

                  {/* =================================================
                      HERITAGE POPUP
                  ================================================= */}

                  <Popup>

                    <div className="heritage-popup">

                      {/* CATEGORY */}

                      <div className="popup-category">

                        {item.category ||
                          "HERITAGE"}

                      </div>

                      {/* NAME */}

                      <h3>
                        {site.name}
                      </h3>

                      {/* LOCATION */}

                      <div className="popup-location">

                        <MapPin
                          size={14}
                        />

                        <span>
                          {getLocation(
                            site
                          )}
                        </span>

                      </div>

                      {/* DESCRIPTION */}

                      {item.description && (
                        <p>
                          {item.description}
                        </p>
                      )}

                      {/* EXPLORE */}

                      <button
                        type="button"

                        onClick={(event) =>{
                        event.stopPropagation();
                        onSelectSite(
                            site
                          )
                        }}
                      >

                        <span>
                          Explore Site
                        </span>

                        <ArrowRight
                          size={14}
                        />

                      </button>

                    </div>

                  </Popup>

                </Marker>
              );
            }
          )}

        </MapContainer>

        {/* =================================================
            MAP OVERLAY
        ================================================= */}

        <div className="map-overlay">

          {/* LIVE */}

          <div className="map-live">

            <span className="live-dot" />

            <span>
              LIVE HERITAGE DATA
            </span>

          </div>

          {/* TITLE */}

          <div className="map-overlay-title">
            3D BHARAT
          </div>

          {/* SUBTITLE */}

          <div className="map-overlay-subtitle">
            Cultural Intelligence Network
          </div>

        </div>

        {/* =================================================
            LEGEND
        ================================================= */}

        <div className="map-legend">

          {/* HERITAGE SITE */}

          <div className="legend-item">

            <span
              className="legend-marker"
            />

            <span>
              Heritage Site
            </span>

          </div>

          {/* NETWORK */}

          <div className="legend-item">

            <Network
              size={14}
            />

            <span>
              Click to explore
            </span>

          </div>

        </div>

      </div>

      {/* =================================================
          NO COORDINATES
      ================================================= */}

      {sites.length > 0 &&
        mappedSites.length === 0 && (

          <div className="map-warning">

            <MapPin
              size={20}
            />

            <div>

              <strong>
                Geographic coordinates unavailable
              </strong>

              <span>
                Your heritage records are loading
                correctly, but latitude and longitude
                are not available for these sites yet.
              </span>

            </div>

          </div>
        )}

      {/* =================================================
          EMPTY DATA
      ================================================= */}

      {sites.length === 0 && (

        <div className="map-warning">

          <MapPin
            size={20}
          />

          <div>

            <strong>
              No heritage sites available
            </strong>

            <span>
              Heritage locations will appear here
              when data is available.
            </span>

          </div>

        </div>
      )}

    </section>
  );
}