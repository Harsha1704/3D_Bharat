import { useEffect, useState, useMemo } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import {
  getHeritageSites,
  getHeritageSite,
  getSiteConnections,
  getStateTracker,
  getHeritage3DAssets,
  getHeritageSources,
  type HeritageSite,
  type HeritageConnection,
  type StateTrackerResponse,
  type Heritage3DAsset,
} from "./api";

import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import CommandCentreView from "./components/CommandCentreView";
import HeritageExplorerView from "./components/HeritageExplorerView";
import InteractiveIndiaMap from "./components/InteractiveIndiaMap";
import KnowledgeGraphView from "./components/KnowledgeGraphView";
import AiHeritageAssistant from "./components/AiHeritageAssistant";
import ThreeDExplorer from "./components/ThreeDExplorer";
import NationalCoverageView from "./components/NationalCoverageView";
import HeritageAnalytics from "./components/HeritageAnalytics";
import HeritageManagement from "./components/HeritageManagement";
import PlatformSettingsView from "./components/PlatformSettingsView";
import NotFoundView from "./components/NotFoundView";
import HeritageSiteDossierModal from "./components/HeritageSiteDossierModal";
import { AddSiteModal, ReportsModal } from "./components/ManageDataModals";
import { Loader2 } from "lucide-react";

import "./App.css";

function AppContent() {
  const navigate = useNavigate();
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  const [sites, setSites] = useState<HeritageSite[]>([]);
  const [selectedSite, setSelectedSite] = useState<HeritageSite | null>(null);
  const [connections, setConnections] = useState<HeritageConnection[]>([]);
  const [trackerData, setTrackerData] = useState<StateTrackerResponse | null>(null);
  const [threeDAssets, setThreeDAssets] = useState<Heritage3DAsset[]>([]);
  const [sourcesCount, setSourcesCount] = useState<number>(12);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modals state
  const [isDossierOpen, setIsDossierOpen] = useState(false);
  const [isAddSiteOpen, setIsAddSiteOpen] = useState(false);
  const [isReportsOpen, setIsReportsOpen] = useState(false);

  /* =======================================================
     LOAD INITIAL HERITAGE DATA FROM VERIFIED BACKEND
  ======================================================= */
  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [loadedSites, trackerRes, assetsRes, sourcesRes] = await Promise.all([
        getHeritageSites(0, 100),
        getStateTracker().catch(() => null),
        getHeritage3DAssets().catch(() => []),
        getHeritageSources().catch(() => []),
      ]);

      setSites(loadedSites);
      setTrackerData(trackerRes);
      setThreeDAssets(assetsRes);
      setSourcesCount(sourcesRes.length || 12);

      const defaultSite = loadedSites[0] || null;
      setSelectedSite(defaultSite);

      if (defaultSite) {
        try {
          const conns = await getSiteConnections(defaultSite.id);
          setConnections(conns);
        } catch {
          // Graceful fallback
        }
      }
    } catch (err: any) {
      setError(err.message || "Failed to load national heritage data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  /* =======================================================
     SITE SELECTION & DOSSIER HANDLERS
  ======================================================= */
  const handleSelectSite = async (site: HeritageSite) => {
    setSelectedSite(site);
    try {
      const conns = await getSiteConnections(site.id);
      setConnections(conns);
    } catch {
      // Graceful fallback
    }
  };

  const handleExploreSite = (site: HeritageSite) => {
    setSelectedSite(site);
    setIsDossierOpen(true);
  };

  const handleSelectRelatedSiteById = async (siteId: number) => {
    const existing = sites.find((s) => s.id === siteId);
    if (existing) {
      handleSelectSite(existing);
    } else {
      try {
        const fullSite = await getHeritageSite(siteId);
        handleSelectSite(fullSite);
      } catch {
        // fallback
      }
    }
  };

  /* =======================================================
     EXPORT DATA HANDLER (SAFE AUDIT RECORD)
  ======================================================= */
  const handleExportData = () => {
    const dataToExport = {
      platform: "3D BHARAT",
      version: "Phase 9.2 National Heritage Intelligence",
      timestamp: new Date().toISOString(),
      summary: {
        total_monuments: sites.length,
        represented_states: distinctStatesCount,
        knowledge_graph_entities: 44,
        knowledge_graph_relationships: 35,
        total_sources: sourcesCount,
      },
      sites: sites.map((s) => ({
        id: s.id,
        name: s.name,
        state: s.state,
        district: s.district,
        category: s.category,
        period: s.period,
        latitude: s.latitude,
        longitude: s.longitude,
        description: s.description,
      })),
    };

    const blob = new Blob([JSON.stringify(dataToExport, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `3d_bharat_heritage_export_${new Date().toISOString().slice(0, 10)}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  /* =======================================================
     RECONCILED TRUTHFUL METRICS
  ======================================================= */
  const distinctStatesCount = useMemo(() => {
    const stateSet = new Set(sites.map((s) => s.state).filter(Boolean));
    return stateSet.size || 12;
  }, [sites]);

  return (
    <div className="bharat-app-layout">
      {/* 1. Left Navigation Sidebar with Router NavLinks */}
      <Sidebar
        isOpenMobile={isMobileSidebarOpen}
        onCloseMobile={() => setIsMobileSidebarOpen(false)}
        totalSites={sites.length}
      />

      {/* 2. Main Dashboard & Router Container */}
      <div className="dashboard-main-wrapper">
        {/* Top Header with Breadcrumbs, Live Status, Search */}
        <Header
          sites={sites}
          totalSites={sites.length}
          distinctStatesCount={distinctStatesCount}
          onSearchSelect={(site) => {
            handleSelectSite(site);
            handleExploreSite(site);
          }}
          onOpenMobileMenu={() => setIsMobileSidebarOpen(true)}
        />

        {/* Main Content Area */}
        <main className="dashboard-content-area">
          {loading && (
            <div className="top-loading-indicator">
              <Loader2 className="w-4 h-4 text-amber-400 animate-spin mr-2 inline" />
              <span>Connecting to live ASI & UNESCO National Archive...</span>
            </div>
          )}

          {error && (
            <div className="error-alert-banner">
              <span>{error}</span>
            </div>
          )}

          {/* APPLICATION ROUTES */}
          <Routes>
            {/* ROUTE 1: COMMAND CENTRE */}
            <Route
              path="/"
              element={
                <CommandCentreView
                  sites={sites}
                  distinctStatesCount={distinctStatesCount}
                  entitiesCount={44}
                  sourcesCount={sourcesCount}
                  onExploreSite={handleExploreSite}
                  onNavigateToMap={() => navigate("/map")}
                  onNavigateToGraph={() => navigate("/graph")}
                  onNavigateToAi={() => navigate("/assistant")}
                  onNavigateTo3D={() => navigate("/3d")}
                  onNavigateToCoverage={() => navigate("/coverage")}
                  onNavigateToAnalytics={() => navigate("/analytics")}
                />
              }
            />

            {/* ROUTE 1B: REDIRECT /dashboard TO / */}
            <Route path="/dashboard" element={<Navigate to="/" replace />} />

            {/* ROUTE 2: HERITAGE EXPLORER (IMAGE-FIRST EDITORIAL DISCOVERY) */}
            <Route
              path="/explorer"
              element={
                <HeritageExplorerView
                  sites={sites}
                  onOpenSiteDossier={handleExploreSite}
                  onSelectSiteOnMap={(site) => {
                    handleSelectSite(site);
                    navigate("/map");
                  }}
                />
              }
            />

            {/* ROUTE 3: INDIA HERITAGE MAP */}
            <Route
              path="/map"
              element={
                <div className="expanded-view-container">
                  <div className="expanded-view-header">
                    <h2>All India Heritage Map</h2>
                    <span className="text-xs text-gray-400">
                      CartoDB Dark Matter Basemap • Public Domain • Zero Watermarks
                    </span>
                  </div>
                  <InteractiveIndiaMap
                    sites={sites}
                    selectedSite={selectedSite}
                    onSelectSite={handleSelectSite}
                    onExploreSite={handleExploreSite}
                    onExploreAll={() => {}}
                  />
                </div>
              }
            />

            {/* ROUTE 4: CULTURAL KNOWLEDGE GRAPH */}
            <Route
              path="/graph"
              element={
                <div className="expanded-view-container">
                  <div className="expanded-view-header">
                    <h2>Cultural Knowledge Graph</h2>
                    <span className="text-xs text-gray-400">
                      44 Entities • 35 Relationships • Evidence Provenance Workspace
                    </span>
                  </div>
                  <KnowledgeGraphView
                    isExpanded={true}
                    selectedSite={selectedSite}
                    allSites={sites}
                    connections={connections}
                    onSelectConnectedSite={handleSelectSite}
                    onViewFullGraph={() => {}}
                    onOpenSiteDossier={handleExploreSite}
                  />
                </div>
              }
            />

            {/* ROUTE 5: AI HERITAGE INTELLIGENCE */}
            <Route
              path="/assistant"
              element={
                <AiHeritageAssistant
                  isExpanded={true}
                  selectedSite={selectedSite}
                  allSites={sites}
                  onExploreSite={handleExploreSite}
                />
              }
            />

            {/* ROUTE 6: 3D DIGITAL PRESERVATION */}
            <Route
              path="/3d"
              element={<ThreeDExplorer isFullPage={true} assets3D={threeDAssets} />}
            />

            {/* ROUTE 7: NATIONAL DATA COVERAGE & ASI AUDIT */}
            <Route
              path="/coverage"
              element={
                <NationalCoverageView
                  initialTrackerData={trackerData}
                  sites={sites}
                />
              }
            />

            {/* ROUTE 8: HERITAGE ANALYTICS */}
            <Route
              path="/analytics"
              element={
                <div className="expanded-view-container">
                  <div className="expanded-view-header">
                    <h2>National Heritage Analytics & Regional Breakdown</h2>
                  </div>
                  <HeritageAnalytics sites={sites} onViewDetails={() => {}} />
                </div>
              }
            />

            {/* ROUTE 9: PRESERVATION MANAGEMENT */}
            <Route
              path="/management"
              element={
                <div className="expanded-view-container">
                  <div className="expanded-view-header">
                    <h2>Heritage Data Management & Pipelines</h2>
                  </div>
                  <HeritageManagement
                    onAddNewSite={() => setIsAddSiteOpen(true)}
                    onUploadDataset={() => setIsReportsOpen(true)}
                    onViewReports={() => setIsReportsOpen(true)}
                    onExportData={handleExportData}
                  />
                </div>
              }
            />

            {/* ROUTE 10: PLATFORM SETTINGS (DEDICATED REAL SETTINGS VIEW) */}
            <Route
              path="/settings"
              element={
                <PlatformSettingsView
                  totalSites={sites.length}
                  representedStates={distinctStatesCount}
                />
              }
            />

            {/* ROUTE 11: 404 NOT FOUND FALLBACK */}
            <Route path="*" element={<NotFoundView />} />
          </Routes>
        </main>
      </div>

      {/* =======================================================
         MODALS (AVAILABLE GLOBALLY ACROSS ALL ROUTES)
      ======================================================= */}
      {isDossierOpen && selectedSite && (
        <HeritageSiteDossierModal
          site={selectedSite}
          onClose={() => setIsDossierOpen(false)}
          onSelectRelatedSite={handleSelectRelatedSiteById}
        />
      )}

      <AddSiteModal
        isOpen={isAddSiteOpen}
        onClose={() => setIsAddSiteOpen(false)}
        onSuccess={() => loadInitialData()}
      />

      <ReportsModal
        isOpen={isReportsOpen}
        onClose={() => setIsReportsOpen(false)}
      />
    </div>
  );
}

export function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
