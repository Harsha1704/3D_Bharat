import { useEffect, useMemo, useState } from "react";

import {
  ArrowLeft,
  ArrowRight,
  Globe2,
  Landmark,
  Network,
  Palette,
  Search,
  Sparkles,
  Utensils,
  Music2,
  PartyPopper,
  ScrollText,
  Link2,
  MapPin,
  Loader2,
  AlertCircle,
} from "lucide-react";

import "./App.css";
import HeritageMap from "./components/HeritageMap";
import {
  getHeritageSites,
  getHeritageSite,
  getSiteConnections,
  type HeritageSite,
  type HeritageConnection,
} from "./api";

/* =========================================================
   CATEGORIES
========================================================= */

const categories = [
  {
    icon: Landmark,
    title: "Heritage",
    text: "Explore monuments, historical places and living heritage.",
  },
  {
    icon: PartyPopper,
    title: "Festivals",
    text: "Discover India's celebrations, rituals and seasonal traditions.",
  },
  {
    icon: Palette,
    title: "Arts & Crafts",
    text: "Explore traditional art forms, crafts and indigenous techniques.",
  },
  {
    icon: Music2,
    title: "Dance & Music",
    text: "Discover India's classical and folk performing traditions.",
  },
  {
    icon: Utensils,
    title: "Cuisine",
    text: "Explore regional food traditions and culinary heritage.",
  },
  {
    icon: ScrollText,
    title: "Traditions",
    text: "Understand customs, practices, stories and cultural knowledge.",
  },
];

/* =========================================================
   REGIONS
========================================================= */

const regions = [
  ["01", "North India", "Punjab • Himachal • Rajasthan • Uttar Pradesh"],
  [
    "02",
    "South India",
    "Tamil Nadu • Kerala • Karnataka • Andhra Pradesh",
  ],
  ["03", "East India", "West Bengal • Odisha • Bihar • Jharkhand"],
  ["04", "West India", "Gujarat • Maharashtra • Goa • Madhya Pradesh"],
  ["05", "Northeast India", "Assam • Sikkim • Meghalaya • Nagaland"],
];

/* =========================================================
   REMOVE DUPLICATE CONNECTIONS
========================================================= */

function removeDuplicateConnections(
  connections: HeritageConnection[]
): HeritageConnection[] {
  const uniqueConnections: HeritageConnection[] = [];
  const seenPairs = new Set<string>();

  for (const connection of connections) {
    const firstId = Math.min(
      connection.source_site_id,
      connection.target_site_id
    );

    const secondId = Math.max(
      connection.source_site_id,
      connection.target_site_id
    );

    const relationship =
      connection.relationship_type || "UNKNOWN";

    const key = `${firstId}-${secondId}-${relationship}`;

    if (!seenPairs.has(key)) {
      seenPairs.add(key);
      uniqueConnections.push(connection);
    }
  }

  return uniqueConnections;
}

/* =========================================================
   KNOWLEDGE GRAPH
========================================================= */

function KnowledgeGraph({
  sites,
  selectedSite,
  onSelectSite,
}: {
  sites: HeritageSite[];
  selectedSite: HeritageSite | null;
  onSelectSite: (site: HeritageSite) => void;
}) {
  const [graphSite, setGraphSite] =
    useState<HeritageSite | null>(
      selectedSite || sites[0] || null
    );

  const [graphConnections, setGraphConnections] =
    useState<HeritageConnection[]>([]);

  const [loadingGraph, setLoadingGraph] =
    useState(false);

  const [graphError, setGraphError] =
    useState<string | null>(null);

  /* -------------------------------------------------------
     If selected site changes, update graph center
  ------------------------------------------------------- */

  useEffect(() => {
    if (selectedSite) {
      setGraphSite(selectedSite);
    }
  }, [selectedSite]);

  /* -------------------------------------------------------
     If sites load later, use first site
  ------------------------------------------------------- */

  useEffect(() => {
    if (!graphSite && sites.length > 0) {
      setGraphSite(sites[0]);
    }
  }, [sites, graphSite]);

  /* -------------------------------------------------------
     Load graph connections
  ------------------------------------------------------- */

  useEffect(() => {
    if (!graphSite) {
      return;
    }

    const currentGraphSite = graphSite;

    async function loadGraph() {
      try {
        setLoadingGraph(true);
        setGraphError(null);

        console.log(
          "Loading graph for:",
          currentGraphSite.name
        );

        const data = await getSiteConnections(
          currentGraphSite.id
        );

        console.log(
          "Graph connections:",
          data
        );

        const uniqueConnections =
          removeDuplicateConnections(data);

        setGraphConnections(uniqueConnections);
      } catch (error) {
        console.error(
          "Failed to load graph connections:",
          error
        );

        setGraphConnections([]);

        setGraphError(
          "Unable to load knowledge graph connections."
        );
      } finally {
        setLoadingGraph(false);
      }
    }

    loadGraph();
  }, [graphSite]);

  /* -------------------------------------------------------
     Empty graph
  ------------------------------------------------------- */

  if (!graphSite) {
    return (
      <div className="knowledge-empty">
        No heritage sites available.
      </div>
    );
  }

  /* -------------------------------------------------------
     Resolve connected sites
  ------------------------------------------------------- */

  const connectedSites = graphConnections
    .map((connection) => {
      const connectedId =
        connection.source_site_id === graphSite.id
          ? connection.target_site_id
          : connection.source_site_id;

      const site = sites.find(
        (item) => item.id === connectedId
      );

      if (!site) {
        return null;
      }

      return {
        site,
        connection,
      };
    })
    .filter(
      (
        item
      ): item is {
        site: HeritageSite;
        connection: HeritageConnection;
      } => item !== null
    );

  /* -------------------------------------------------------
     SVG dimensions
  ------------------------------------------------------- */

  const width = 700;
  const height = 500;

  const centerX = width / 2;
  const centerY = height / 2;

  /* -------------------------------------------------------
     Position nodes
  ------------------------------------------------------- */

  const nodes = connectedSites.map(
    (item, index) => {
      const total = connectedSites.length;

      const angle =
        (index / Math.max(total, 1)) *
        Math.PI *
        2 -
        Math.PI / 2;

      const radius =
        total <= 2
          ? 170
          : total <= 4
            ? 190
            : 210;

      return {
        ...item,
        x:
          centerX +
          Math.cos(angle) * radius,
        y:
          centerY +
          Math.sin(angle) * radius,
      };
    }
  );

  /* -------------------------------------------------------
     Select graph node
  ------------------------------------------------------- */

  function selectNode(site: HeritageSite) {
    setGraphSite(site);
    onSelectSite(site);
  }

  /* -------------------------------------------------------
     RENDER
  ------------------------------------------------------- */

  return (
    <div className="real-knowledge-graph">

      {/* GRAPH HEADER */}

      <div className="graph-header">

        <div>
          <span className="graph-live-label">
            LIVE KNOWLEDGE GRAPH
          </span>

          <h3>
            Cultural relationships
          </h3>

          <p>
            Relationships are generated directly
            from the 3D BHARAT backend.
          </p>
        </div>

        <div className="graph-stat">
          <strong>
            {connectedSites.length}
          </strong>

          <span>
            Connections
          </span>
        </div>

      </div>

      {/* GRAPH CANVAS */}

      <div className="graph-canvas">

        {/* LOADING */}

        {loadingGraph && (
          <div className="graph-loading">

            <Loader2
              size={25}
              className="spin"
            />

            <span>
              Building cultural graph...
            </span>

          </div>
        )}

        {/* ERROR */}

        {graphError && (
          <div className="graph-error">

            <AlertCircle size={18} />

            <span>
              {graphError}
            </span>

          </div>
        )}

        {/* NO CONNECTIONS */}

        {!loadingGraph &&
          !graphError &&
          connectedSites.length === 0 && (
            <div className="graph-no-connections">

              <Network size={34} />

              <strong>
                No connections yet
              </strong>

              <span>
                This heritage site does not have
                any relationships in the database.
              </span>

            </div>
          )}

        {/* SVG GRAPH */}

        {!loadingGraph &&
          !graphError &&
          connectedSites.length > 0 && (

            <svg
              className="knowledge-svg"
              viewBox={`0 0 ${width} ${height}`}
              preserveAspectRatio="xMidYMid meet"
            >

              {/* CONNECTION LINES */}

              {nodes.map(
                ({
                  connection,
                  x,
                  y,
                }) => (

                  <g
                    key={`edge-${connection.id}`}
                  >

                    <line
                      x1={centerX}
                      y1={centerY}
                      x2={x}
                      y2={y}
                      className="graph-edge"
                    />

                    {/* RELATIONSHIP LABEL */}

                    <text
                      x={
                        centerX +
                        (x - centerX) *
                        0.52
                      }
                      y={
                        centerY +
                        (y - centerY) *
                        0.52 -
                        8
                      }
                      textAnchor="middle"
                      className="graph-edge-label"
                    >
                      {(
                        connection.relationship_type ||
                        "connection"
                      )
                        .replace(/_/g, " ")
                        .toLowerCase()}
                    </text>

                    {/* CONFIDENCE */}

                    <text
                      x={
                        centerX +
                        (x - centerX) *
                        0.52
                      }
                      y={
                        centerY +
                        (y - centerY) *
                        0.52 +
                        10
                      }
                      textAnchor="middle"
                      className="graph-confidence"
                    >
                      {(
                        Math.max(
                          0,
                          Math.min(
                            connection.confidence_score,
                            1
                          )
                        ) * 100
                      ).toFixed(1)}
                      %
                    </text>

                  </g>
                )
              )}

              {/* CONNECTED NODES */}

              {nodes.map(
                ({
                  site,
                  connection,
                  x,
                  y,
                }) => (

                  <g
                    key={`node-${site.id}`}
                    className="graph-site-node"
                    onClick={() =>
                      selectNode(site)
                    }
                  >

                    <circle
                      cx={x}
                      cy={y}
                      r="42"
                      className="graph-node-circle"
                    />

                    <circle
                      cx={x}
                      cy={y}
                      r="34"
                      className="graph-node-inner"
                    />

                    <text
                      x={x}
                      y={y - 3}
                      textAnchor="middle"
                      className="graph-node-icon-text"
                    >
                      {site.name
                        .substring(0, 1)
                        .toUpperCase()}
                    </text>

                    <text
                      x={x}
                      y={y + 62}
                      textAnchor="middle"
                      className="graph-site-name"
                    >
                      {site.name.length > 20
                        ? `${site.name.substring(
                          0,
                          20
                        )}...`
                        : site.name}
                    </text>

                    <text
                      x={x}
                      y={y + 79}
                      textAnchor="middle"
                      className="graph-site-location"
                    >
                      {site.city ||
                        site.state ||
                        "India"}
                    </text>

                  </g>
                )
              )}

              {/* CENTER NODE */}

              <g
                className="graph-center-node"
                onClick={() =>
                  onSelectSite(graphSite)
                }
              >

                <circle
                  cx={centerX}
                  cy={centerY}
                  r="66"
                  className="graph-center-glow"
                />

                <circle
                  cx={centerX}
                  cy={centerY}
                  r="55"
                  className="graph-center-circle"
                />

                <circle
                  cx={centerX}
                  cy={centerY}
                  r="46"
                  className="graph-center-inner"
                />

                <text
                  x={centerX}
                  y={centerY - 7}
                  textAnchor="middle"
                  className="graph-center-title"
                >
                  {graphSite.name.length > 15
                    ? `${graphSite.name.substring(
                      0,
                      15
                    )}...`
                    : graphSite.name}
                </text>

                <text
                  x={centerX}
                  y={centerY + 13}
                  textAnchor="middle"
                  className="graph-center-location"
                >
                  {graphSite.city ||
                    graphSite.state ||
                    "Bharat"}
                </text>

              </g>

            </svg>
          )}

      </div>

      {/* GRAPH LEGEND */}

      <div className="graph-legend">

        <div>
          <span className="legend-dot center"></span>
          Selected Heritage Site
        </div>

        <div>
          <span className="legend-dot"></span>
          Connected Heritage
        </div>

        <div>
          <Network size={14} />
          Click a node to explore
        </div>

      </div>

    </div>
  );
}

/* =========================================================
   MAIN APP
========================================================= */

function App() {

  /* =======================================================
     STATE
  ======================================================= */

  const [sites, setSites] =
    useState<HeritageSite[]>([]);

  const [selectedSite, setSelectedSite] =
    useState<HeritageSite | null>(null);

  const [connections, setConnections] =
    useState<HeritageConnection[]>([]);

  const [loadingSites, setLoadingSites] =
    useState(true);

  const [loadingConnections, setLoadingConnections] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const [connectionError, setConnectionError] =
    useState<string | null>(null);

  const [searchQuery, setSearchQuery] =
    useState("");

  /* =======================================================
     LOAD HERITAGE SITES
  ======================================================= */

  useEffect(() => {
    loadSites();
  }, []);

  async function loadSites() {
    try {
      setLoadingSites(true);
      setError(null);

      const data =
        await getHeritageSites();

      console.log(
        "LIVE HERITAGE SITES:",
        data
      );

      setSites(data);

    } catch (err) {

      console.error(
        "Failed to load heritage sites:",
        err
      );

      setError(
        "Unable to connect to the 3D BHARAT backend."
      );

    } finally {
      setLoadingSites(false);
    }
  }

  /* =======================================================
     OPEN SITE
  ======================================================= */

  async function openSite(
    site: HeritageSite
  ) {

    console.log(
      "Opening site:",
      site
    );

    setSelectedSite(site);
    setConnections([]);
    setConnectionError(null);
    setLoadingConnections(true);

    try {

      /* ---------------------------------------------------
         Fetch latest site details
      --------------------------------------------------- */

      let fullSite = site;

      try {

        fullSite =
          await getHeritageSite(
            site.id
          );

      } catch (siteError) {

        console.warn(
          "Could not fetch latest site information. Using existing site.",
          siteError
        );

      }

      setSelectedSite(fullSite);

      /* ---------------------------------------------------
         Fetch connections
      --------------------------------------------------- */

      console.log(
        `Fetching connections for site ${site.id}`
      );

      const data =
        await getSiteConnections(
          site.id
        );

      console.log(
        `Connections for ${site.name}:`,
        data
      );

      /* ---------------------------------------------------
         Remove duplicate relationships
      --------------------------------------------------- */

      const uniqueConnections =
        removeDuplicateConnections(
          data
        );

      setConnections(
        uniqueConnections
      );

      /* ---------------------------------------------------
         Scroll to details
      --------------------------------------------------- */

      requestAnimationFrame(() => {

        setTimeout(() => {

          const details =
            document.getElementById(
              "site-details"
            );

          if (details) {

            details.scrollIntoView({
              behavior: "smooth",
              block: "start",
            });

          }

        }, 100);

      });

    } catch (err) {

      console.error(
        "Failed to load cultural connections:",
        err
      );

      setConnectionError(
        "Unable to load cultural connections from the backend."
      );

    } finally {

      setLoadingConnections(false);

    }
  }

  /* =======================================================
     CLOSE SITE
  ======================================================= */

  function closeSite() {

    setSelectedSite(null);
    setConnections([]);
    setConnectionError(null);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  /* =======================================================
     FIND CONNECTED SITE
  ======================================================= */

  function getConnectedSite(
    connection: HeritageConnection
  ): HeritageSite | undefined {

    if (!selectedSite) {
      return undefined;
    }

    const connectedId =
      connection.source_site_id ===
        selectedSite.id
        ? connection.target_site_id
        : connection.source_site_id;

    return sites.find(
      (site) =>
        site.id === connectedId
    );
  }

  /* =======================================================
     SEARCH
  ======================================================= */

  const filteredSites =
    useMemo(() => {

      const query =
        searchQuery
          .trim()
          .toLowerCase();

      if (!query) {
        return sites;
      }

      return sites.filter(
        (site) => {

          return (
            site.name
              ?.toLowerCase()
              .includes(query) ||

            site.state
              ?.toLowerCase()
              .includes(query) ||

            site.city
              ?.toLowerCase()
              .includes(query) ||

            site.district
              ?.toLowerCase()
              .includes(query) ||

            site.category
              ?.toLowerCase()
              .includes(query) ||

            site.period
              ?.toLowerCase()
              .includes(query)
          );
        }
      );

    }, [sites, searchQuery]);

  /* =======================================================
     FORMAT RELATIONSHIP
  ======================================================= */

  function formatRelationship(
    relationship?: string
  ) {

    if (!relationship) {
      return "Cultural Connection";
    }

    return relationship
      .replace(/_/g, " ")
      .toLowerCase()
      .replace(
        /\b\w/g,
        (letter) =>
          letter.toUpperCase()
      );
  }

  /* =======================================================
     LOCATION
  ======================================================= */

  function getLocation(
    site: HeritageSite
  ) {

    const city =
      site.city ||
      site.district ||
      "";

    const state =
      site.state ||
      "";

    if (city && state) {
      return `${city}, ${state}`;
    }

    return (
      city ||
      state ||
      "India"
    );
  }

  /* =======================================================
     RENDER
  ======================================================= */

  return (
    <div className="app">

      {/* =================================================
          NAVBAR
      ================================================= */}

      <header className="navbar">

        <div className="brand">

          <div className="brand-mark">
            <Globe2 size={20} />
          </div>

          <div>

            <div className="brand-name">
              3D BHARAT
            </div>

            <div className="brand-subtitle">
              CULTURAL INTELLIGENCE
            </div>

          </div>

        </div>

        <nav className="nav-links">

          <a href="#explore">
            Explore
          </a>

          <a href="#heritage">
            Heritage
          </a>

          <a href="#regions">
            Regions
          </a>

          <a href="#knowledge">
            Knowledge Graph
          </a>

        </nav>

        {/* SEARCH */}

        <div className="nav-search">

          <Search size={17} />

          <input
            type="text"
            placeholder="Search heritage..."
            value={searchQuery}
            onChange={(event) =>
              setSearchQuery(
                event.target.value
              )
            }
          />

        </div>

      </header>

      {/* =================================================
          ERROR
      ================================================= */}

      {error && (

        <div className="error-banner">

          <AlertCircle size={18} />

          <span>
            {error}
          </span>

          <button
            type="button"
            onClick={loadSites}
          >
            Retry
          </button>

        </div>

      )}

      {/* =================================================
          MAIN
      ================================================= */}

      <main>

        {/* =================================================
            HERO
        ================================================= */}

        <section className="hero">

          <div className="hero-content">

            <div className="eyebrow">

              <Sparkles size={14} />

              DIGITAL CULTURAL HERITAGE PLATFORM

            </div>

            <h1>

              India,

              <br />

              <span>
                Beyond History.
              </span>

            </h1>

            <p className="hero-description">

              Discover the living heritage of India
              through its traditions, festivals, arts,
              architecture, music, cuisine and stories —
              connected through one intelligent cultural
              platform.

            </p>

            <div className="hero-actions">

              <button
                type="button"
                className="primary-button"
                onClick={() =>
                  document
                    .getElementById(
                      "live-sites"
                    )
                    ?.scrollIntoView({
                      behavior: "smooth",
                    })
                }
              >

                Explore India's Heritage

                <ArrowRight size={17} />

              </button>

              <button
                type="button"
                className="secondary-button"
                onClick={() =>
                  document
                    .getElementById(
                      "knowledge"
                    )
                    ?.scrollIntoView({
                      behavior: "smooth",
                    })
                }
              >

                <Network size={17} />

                Discover Connections

              </button>

            </div>

            <div className="hero-stats">

              <div>

                <strong>
                  {sites.length || "28+"}
                </strong>

                <span>
                  Heritage Sites
                </span>

              </div>

              <div>

                <strong>
                  5000+
                </strong>

                <span>
                  Years of Heritage
                </span>

              </div>

              <div>

                <strong>
                  ∞
                </strong>

                <span>
                  Cultural Stories
                </span>

              </div>

            </div>

          </div>

          {/* HERO VISUAL */}

          <div className="hero-visual">

            <div className="orbit orbit-one"></div>

            <div className="orbit orbit-two"></div>

            <div className="orbit orbit-three"></div>

            <div className="india-core">

              <div className="core-ring">

                <Globe2
                  size={62}
                  strokeWidth={1}
                />

              </div>

              <strong>
                BHARAT
              </strong>

              <span>
                एक • अनेक • अनंत
              </span>

            </div>

            <div className="floating-node node-one">

              <Landmark size={16} />

              <span>
                Heritage
              </span>

            </div>

            <div className="floating-node node-two">

              <Palette size={16} />

              <span>
                Art
              </span>

            </div>

            <div className="floating-node node-three">

              <Music2 size={16} />

              <span>
                Music
              </span>

            </div>

            <div className="floating-node node-four">

              <PartyPopper size={16} />

              <span>
                Festivals
              </span>

            </div>

          </div>

        </section>

        {/* =================================================
            EXPLORE
        ================================================= */}

        <section
          className="section"
          id="explore"
        >

          <div className="section-heading">

            <div>

              <div className="section-label">
                EXPLORE
              </div>

              <h2>

                One civilization.

                <br />

                Thousands of stories.

              </h2>

            </div>

            <p>

              India's cultural identity is not a
              single story. It is a constantly evolving
              network of people, places, traditions and
              knowledge.

            </p>

          </div>

          <div
            className="category-grid"
            id="heritage"
          >

            {categories.map(
              (category, index) => {

                const Icon =
                  category.icon;

                return (

                  <article
                    className="category-card"
                    key={category.title}
                  >

                    <div className="card-icon">

                      <Icon size={21} />

                    </div>

                    <div className="card-number">

                      0{index + 1}

                    </div>

                    <h3>

                      {category.title}

                    </h3>

                    <p>

                      {category.text}

                    </p>

                    <button
                      type="button"
                      onClick={() =>
                        document
                          .getElementById(
                            "live-sites"
                          )
                          ?.scrollIntoView({
                            behavior: "smooth",
                          })
                      }
                    >

                      Explore

                      <ArrowRight size={14} />

                    </button>

                  </article>

                );
              }
            )}

          </div>

        </section>

        {/* =================================================
            LIVE DATABASE
        ================================================= */}

        <section
          className="section live-database"
          id="live-sites"
        >

          <div className="section-heading">

            <div>

              <div className="section-label">
                LIVE DATABASE
              </div>

              <h2>

                Heritage sites

                <br />

                connected to Bharat.

              </h2>

            </div>

            <p>

              These locations are coming directly
              from the 3D BHARAT backend.

            </p>

          </div>

          {/* LOADING */}

          {loadingSites && (

            <div className="loading-state">

              <Loader2
                size={28}
                className="spin"
              />

              <span>
                Loading heritage sites...
              </span>

            </div>

          )}

          {/* DATABASE */}

          {!loadingSites && (

            <div className="database-grid">

              {filteredSites.map(
                (site, index) => (

                  <article
                    className="database-card"
                    key={site.id}
                  >

                    <div className="database-top">

                      <span className="database-number">

                        {String(
                          index + 1
                        ).padStart(2, "0")}

                      </span>

                      <span className="database-category">

                        {site.category ||
                          "Heritage"}

                      </span>

                    </div>

                    <h3>
                      {site.name}
                    </h3>

                    <div className="site-location">

                      <MapPin size={15} />

                      {getLocation(site)}

                    </div>

                    <p>

                      {site.description ||
                        "Discover the cultural heritage of this remarkable Indian site."}

                    </p>

                    <button
                      type="button"
                      className="connection-button"
                      onClick={() =>
                        openSite(site)
                      }
                    >

                      View Connections

                      <Link2 size={15} />

                    </button>

                  </article>

                )
              )}

            </div>

          )}

          {/* EMPTY SEARCH */}

          {!loadingSites &&
            filteredSites.length === 0 && (

              <div className="empty-state">

                No heritage sites found.

              </div>

            )}

        </section>

        {/* =================================================
            SITE DETAILS
        ================================================= */}

        {selectedSite && (

          <section
            className="section site-details"
            id="site-details"
          >

            {/* BACK */}

            <button
              type="button"
              className="back-button"
              onClick={closeSite}
            >

              <ArrowLeft size={17} />

              Back to Heritage Sites

            </button>

            {/* HEADER */}

            <div className="site-detail-header">

              <div>

                <div className="section-label">

                  CULTURAL CONNECTIONS

                </div>

                <h2>
                  {selectedSite.name}
                </h2>

                <div className="detail-location">

                  <MapPin size={16} />

                  {getLocation(
                    selectedSite
                  )}

                </div>

              </div>

              <div className="detail-icon">

                <Landmark size={32} />

              </div>

            </div>

            {/* DESCRIPTION */}

            <div className="site-description">

              <p>

                {selectedSite.description ||
                  "Discover the cultural significance of this heritage site."}

              </p>

              {selectedSite.significance && (

                <div>

                  <strong>
                    Significance
                  </strong>

                  <p>
                    {selectedSite.significance}
                  </p>

                </div>

              )}

            </div>

            {/* CONNECTION LOADING */}

            {loadingConnections && (

              <div className="loading-state">

                <Loader2
                  size={28}
                  className="spin"
                />

                <span>
                  Discovering cultural
                  connections...
                </span>

              </div>

            )}

            {/* CONNECTION ERROR */}

            {!loadingConnections &&
              connectionError && (

                <div className="connection-error">

                  <AlertCircle size={20} />

                  <span>
                    {connectionError}
                  </span>

                  <button
                    type="button"
                    onClick={() =>
                      openSite(
                        selectedSite
                      )
                    }
                  >
                    Try Again
                  </button>

                </div>

              )}

            {/* CONNECTIONS */}

            {!loadingConnections &&
              !connectionError && (

                <div className="connections-container">

                  <div className="connections-heading">

                    <div>

                      <span>
                        CONNECTED HERITAGE
                      </span>

                      <h3>
                        Cultural relationships
                      </h3>

                    </div>

                    <div className="connection-count">

                      {connections.length}

                    </div>

                  </div>

                  {connections.length === 0 ? (

                    <div className="empty-state">

                      <Network size={30} />

                      <span>

                        No cultural connections
                        found for this site yet.

                      </span>

                    </div>

                  ) : (

                    <div className="connections-grid">

                      {connections.map(
                        (connection) => {

                          const connectedSite =
                            getConnectedSite(
                              connection
                            );

                          const confidence =
                            Math.max(
                              0,
                              Math.min(
                                connection.confidence_score,
                                1
                              )
                            );

                          return (

                            <article
                              className="connection-card"
                              key={connection.id}
                            >

                              <div className="connection-card-icon">

                                <Network size={20} />

                              </div>

                              <div className="connection-card-content">

                                <span className="connection-type">

                                  {formatRelationship(
                                    connection.relationship_type
                                  )}

                                </span>

                                <h3>

                                  {connectedSite?.name ||
                                    `Heritage Site #${connection.source_site_id ===
                                      selectedSite.id
                                      ? connection.target_site_id
                                      : connection.source_site_id
                                    }`}

                                </h3>

                                {connectedSite && (

                                  <div className="connected-location">

                                    <MapPin size={14} />

                                    {getLocation(
                                      connectedSite
                                    )}

                                  </div>

                                )}

                                <p>

                                  {connection.description ||
                                    "Cultural relationship discovered through the heritage intelligence system."}

                                </p>

                                <div className="confidence">

                                  <div>

                                    <span>
                                      Confidence
                                    </span>

                                    <strong>

                                      {(
                                        confidence *
                                        100
                                      ).toFixed(1)}
                                      %

                                    </strong>

                                  </div>

                                  <div className="confidence-bar">

                                    <div
                                      style={{
                                        width: `${confidence * 100}%`,
                                      }}
                                    />

                                  </div>

                                </div>

                                {connectedSite && (

                                  <button
                                    type="button"
                                    className="connected-site-button"
                                    onClick={() =>
                                      openSite(
                                        connectedSite
                                      )
                                    }
                                  >

                                    Explore{" "}

                                    {
                                      connectedSite.name
                                    }

                                    <ArrowRight
                                      size={15}
                                    />

                                  </button>

                                )}

                              </div>

                            </article>

                          );
                        }
                      )}

                    </div>

                  )}

                </div>

              )}

          </section>

        )}
        {/* =================================================
            HERITAGE MAP
          ================================================= */}

        <HeritageMap
          sites={sites}
          selectedSite={selectedSite}
          onSelectSite={(site) => {
            openSite(site);
          }}
        />

        {/* =================================================
            REGIONS
        ================================================= */}

        <section
          className="section regions-section"
          id="regions"
        >

          <div className="section-heading">

            <div>

              <div className="section-label">
                REGIONS OF INDIA
              </div>

              <h2>

                Explore culture

                <br />

                by region.

              </h2>

            </div>

            <p>

              Move across India's diverse cultural
              landscape and uncover the traditions
              that make every region unique.

            </p>

          </div>

          <div className="regions-list">

            {regions.map(
              ([number, title, description]) => (

                <button
                  type="button"
                  className="region-row"
                  key={title}
                >

                  <span className="region-number">
                    {number}
                  </span>

                  <div className="region-info">

                    <strong>
                      {title}
                    </strong>

                    <span>
                      {description}
                    </span>

                  </div>

                  <ArrowRight size={19} />

                </button>

              )
            )}

          </div>

        </section>

        {/* =================================================
            KNOWLEDGE GRAPH
        ================================================= */}

        <section
          className="knowledge-section"
          id="knowledge"
        >

          <div className="knowledge-content">

            <div className="section-label">

              CULTURAL KNOWLEDGE GRAPH

            </div>

            <h2>

              Culture is not a collection.

              <br />

              <span>
                It is a connection.
              </span>

            </h2>

            <p>

              Explore relationships between India's
              heritage sites using connections generated
              directly from the 3D BHARAT cultural
              intelligence backend.

            </p>

            <button
              type="button"
              className="primary-button"
              onClick={() =>
                document
                  .getElementById(
                    "live-sites"
                  )
                  ?.scrollIntoView({
                    behavior: "smooth",
                  })
              }
            >

              Explore Heritage Network

              <Network size={17} />

            </button>

          </div>

          <KnowledgeGraph
            sites={sites}
            selectedSite={selectedSite}
            onSelectSite={(site) => {
              openSite(site);
            }}
          />

        </section>

      </main>

      {/* =================================================
          FOOTER
      ================================================= */}

      <footer>

        <div className="brand">

          <div className="brand-mark">

            <Globe2 size={17} />

          </div>

          <div className="brand-name">

            3D BHARAT

          </div>

        </div>

        <span>

          Preserving yesterday.
          Understanding today.
          Inspiring tomorrow.

        </span>

      </footer>

    </div>
  );
}

export default App; 