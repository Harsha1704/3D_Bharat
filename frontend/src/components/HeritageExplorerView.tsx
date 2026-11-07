import React, { useState, useMemo } from "react";
import {
  Compass,
  Search,
  Filter,
  Grid3X3,
  List,
  MapPin,
  Calendar,
  ShieldCheck,
  Landmark,
  ArrowUpDown,
  X,
  Eye,
} from "lucide-react";
import type { HeritageSite } from "../api";

interface HeritageExplorerViewProps {
  sites: HeritageSite[];
  onOpenSiteDossier: (site: HeritageSite) => void;
  onSelectSiteOnMap: (site: HeritageSite) => void;
}

// Category theme badges
const CATEGORY_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  temple: { bg: "rgba(217, 164, 65, 0.15)", text: "#E5AD55", border: "rgba(217, 164, 65, 0.3)" },
  fort: { bg: "rgba(231, 111, 81, 0.15)", text: "#E76F51", border: "rgba(231, 111, 81, 0.3)" },
  cave: { bg: "rgba(56, 189, 248, 0.15)", text: "#38BDF8", border: "rgba(56, 189, 248, 0.3)" },
  monument: { bg: "rgba(244, 162, 97, 0.15)", text: "#F4A261", border: "rgba(244, 162, 97, 0.3)" },
  stupa: { bg: "rgba(241, 196, 15, 0.15)", text: "#F1C40F", border: "rgba(241, 196, 15, 0.3)" },
};

function getCategoryBadge(cat?: string | null) {
  const normalized = (cat || "monument").toLowerCase();
  for (const [key, val] of Object.entries(CATEGORY_COLORS)) {
    if (normalized.includes(key)) return val;
  }
  return { bg: "rgba(217, 164, 65, 0.15)", text: "#D9A441", border: "rgba(217, 164, 65, 0.3)" };
}

export const HeritageExplorerView: React.FC<HeritageExplorerViewProps> = ({
  sites,
  onOpenSiteDossier,
  onSelectSiteOnMap,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");
  const [selectedState, setSelectedState] = useState<string>("ALL");
  const [selectedPeriod, setSelectedPeriod] = useState<string>("ALL");
  const [viewMode, setViewMode] = useState<"grid" | "table">("grid");
  const [sortBy, setSortBy] = useState<"name" | "state" | "category">("name");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  // Derive distinct categories, states, and periods
  const { categories, states, periods } = useMemo(() => {
    const catSet = new Set<string>();
    const stateSet = new Set<string>();
    const periodSet = new Set<string>();

    sites.forEach((s) => {
      if (s.category) catSet.add(s.category);
      if (s.state) stateSet.add(s.state);
      if (s.period) periodSet.add(s.period);
    });

    return {
      categories: Array.from(catSet).sort(),
      states: Array.from(stateSet).sort(),
      periods: Array.from(periodSet).sort(),
    };
  }, [sites]);

  // Filter & sort sites
  const filteredSites = useMemo(() => {
    return sites
      .filter((site) => {
        // Search term filter
        if (searchTerm.trim()) {
          const q = searchTerm.toLowerCase();
          const matchName = site.name.toLowerCase().includes(q);
          const matchState = site.state?.toLowerCase().includes(q) ?? false;
          const matchCity = site.city?.toLowerCase().includes(q) ?? false;
          const matchDistrict = site.district?.toLowerCase().includes(q) ?? false;
          const matchCategory = site.category?.toLowerCase().includes(q) ?? false;
          const matchDesc = site.description?.toLowerCase().includes(q) ?? false;
          if (!matchName && !matchState && !matchCity && !matchDistrict && !matchCategory && !matchDesc) {
            return false;
          }
        }
        // Category filter
        if (selectedCategory !== "ALL" && site.category !== selectedCategory) {
          return false;
        }
        // State filter
        if (selectedState !== "ALL" && site.state !== selectedState) {
          return false;
        }
        // Period filter
        if (selectedPeriod !== "ALL" && site.period !== selectedPeriod) {
          return false;
        }
        return true;
      })
      .sort((a, b) => {
        let valA = "";
        let valB = "";
        if (sortBy === "name") {
          valA = a.name.toLowerCase();
          valB = b.name.toLowerCase();
        } else if (sortBy === "state") {
          valA = (a.state || "").toLowerCase();
          valB = (b.state || "").toLowerCase();
        } else if (sortBy === "category") {
          valA = (a.category || "").toLowerCase();
          valB = (b.category || "").toLowerCase();
        }
        if (valA < valB) return sortOrder === "asc" ? -1 : 1;
        if (valA > valB) return sortOrder === "asc" ? 1 : -1;
        return 0;
      });
  }, [sites, searchTerm, selectedCategory, selectedState, selectedPeriod, sortBy, sortOrder]);

  const toggleSort = (col: "name" | "state" | "category") => {
    if (sortBy === col) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(col);
      setSortOrder("asc");
    }
  };

  return (
    <div className="heritage-explorer-container">
      {/* Explorer Header */}
      <div className="explorer-header-bar">
        <div>
          <div className="flex items-center gap-2">
            <Compass className="w-5 h-5 text-amber-400" />
            <h2 className="text-xl font-bold text-white tracking-wide">Heritage Explorer</h2>
            <span className="count-pill">{filteredSites.length} of {sites.length} Sites</span>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Browse, filter, and inspect verified national monuments, architectural wonders, and archaeological sites.
          </p>
        </div>

        {/* View Toggle */}
        <div className="view-mode-toggle">
          <button
            className={`toggle-btn ${viewMode === "grid" ? "active" : ""}`}
            onClick={() => setViewMode("grid")}
            title="Grid View"
          >
            <Grid3X3 className="w-4 h-4" />
            <span className="text-xs font-medium hidden sm:inline">Grid</span>
          </button>
          <button
            className={`toggle-btn ${viewMode === "table" ? "active" : ""}`}
            onClick={() => setViewMode("table")}
            title="Table View"
          >
            <List className="w-4 h-4" />
            <span className="text-xs font-medium hidden sm:inline">Table</span>
          </button>
        </div>
      </div>

      {/* Filter & Search Toolbar */}
      <div className="explorer-toolbar">
        {/* Search */}
        <div className="explorer-search-wrapper">
          <Search className="w-4 h-4 text-gray-400 search-icon" />
          <input
            type="text"
            className="explorer-search-input"
            placeholder="Search monument by name, state, architecture..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          {searchTerm && (
            <button
              className="clear-search-btn"
              onClick={() => setSearchTerm("")}
              title="Clear search"
            >
              <X className="w-3.5 h-3.5 text-gray-400 hover:text-white" />
            </button>
          )}
        </div>

        {/* Dropdowns */}
        <div className="explorer-dropdowns-group">
          {/* Category Filter */}
          <div className="filter-select-wrapper">
            <Filter className="w-3.5 h-3.5 text-amber-400 mr-1.5" />
            <select
              className="explorer-select"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="ALL">All Categories ({categories.length})</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* State Filter */}
          <div className="filter-select-wrapper">
            <MapPin className="w-3.5 h-3.5 text-cyan-400 mr-1.5" />
            <select
              className="explorer-select"
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
            >
              <option value="ALL">All States ({states.length})</option>
              {states.map((st) => (
                <option key={st} value={st}>
                  {st}
                </option>
              ))}
            </select>
          </div>

          {/* Period Filter */}
          <div className="filter-select-wrapper">
            <Calendar className="w-3.5 h-3.5 text-emerald-400 mr-1.5" />
            <select
              className="explorer-select"
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
            >
              <option value="ALL">All Periods ({periods.length})</option>
              {periods.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Active Filter Chips */}
      {(searchTerm || selectedCategory !== "ALL" || selectedState !== "ALL" || selectedPeriod !== "ALL") && (
        <div className="active-filters-row">
          <span className="text-xs text-gray-400">Active filters:</span>
          {searchTerm && (
            <span className="active-filter-badge" onClick={() => setSearchTerm("")}>
              Query: "{searchTerm}" <X className="w-3 h-3 ml-1 inline" />
            </span>
          )}
          {selectedCategory !== "ALL" && (
            <span className="active-filter-badge" onClick={() => setSelectedCategory("ALL")}>
              Category: {selectedCategory} <X className="w-3 h-3 ml-1 inline" />
            </span>
          )}
          {selectedState !== "ALL" && (
            <span className="active-filter-badge" onClick={() => setSelectedState("ALL")}>
              State: {selectedState} <X className="w-3 h-3 ml-1 inline" />
            </span>
          )}
          {selectedPeriod !== "ALL" && (
            <span className="active-filter-badge" onClick={() => setSelectedPeriod("ALL")}>
              Period: {selectedPeriod} <X className="w-3 h-3 ml-1 inline" />
            </span>
          )}
          <button
            className="text-xs text-amber-400 hover:underline ml-2"
            onClick={() => {
              setSearchTerm("");
              setSelectedCategory("ALL");
              setSelectedState("ALL");
              setSelectedPeriod("ALL");
            }}
          >
            Reset All
          </button>
        </div>
      )}

      {/* Main Content Area */}
      {filteredSites.length === 0 ? (
        <div className="empty-explorer-state">
          <Landmark className="w-12 h-12 text-amber-400/40 mb-3" />
          <h4 className="text-base font-semibold text-white">No Heritage Sites Match Your Filter</h4>
          <p className="text-xs text-gray-400 mt-1 max-w-md text-center">
            Try adjusting your search query, or clear selected state and category filters to browse the complete national catalogue.
          </p>
        </div>
      ) : viewMode === "grid" ? (
        /* GRID VIEW */
        <div className="explorer-grid">
          {filteredSites.map((site) => {
            const badge = getCategoryBadge(site.category);
            const locationStr = [site.city || site.district, site.state].filter(Boolean).join(", ");
            return (
              <div key={site.id} className="explorer-card group">
                <div className="explorer-card-header">
                  <div className="flex items-center justify-between w-full">
                    <span
                      className="category-badge-chip"
                      style={{
                        backgroundColor: badge.bg,
                        color: badge.text,
                        borderColor: badge.border,
                      }}
                    >
                      {site.category || "Monument"}
                    </span>
                    <span className="verified-badge-chip">
                      <ShieldCheck className="w-3 h-3 text-emerald-400 inline mr-1" />
                      Verified
                    </span>
                  </div>
                  <h3 className="explorer-card-title">{site.name}</h3>
                  <div className="explorer-card-meta">
                    <MapPin className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                    <span>{locationStr || "Bharat"}</span>
                  </div>
                </div>

                <div className="explorer-card-body">
                  <p className="explorer-card-desc">
                    {site.description || "Historical monument and cultural landmark of national significance."}
                  </p>

                  {site.period && (
                    <div className="explorer-card-era">
                      <Calendar className="w-3.5 h-3.5 text-gray-400 mr-1.5" />
                      <span className="text-xs text-gray-300">Period: {site.period}</span>
                    </div>
                  )}

                  {site.tags && site.tags.length > 0 && (
                    <div className="explorer-card-tags">
                      {site.tags.slice(0, 3).map((tag, idx) => (
                        <span key={idx} className="explorer-tag">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="explorer-card-footer">
                  <button
                    className="explorer-action-btn secondary"
                    onClick={() => onSelectSiteOnMap(site)}
                    title="Locate on Map"
                  >
                    <MapPin className="w-3.5 h-3.5" />
                    <span>Map</span>
                  </button>
                  <button
                    className="explorer-action-btn primary"
                    onClick={() => onOpenSiteDossier(site)}
                    title="View Complete Archaeological Dossier"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>Dossier</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* TABLE VIEW */
        <div className="explorer-table-container">
          <table className="explorer-table">
            <thead>
              <tr>
                <th onClick={() => toggleSort("name")} className="cursor-pointer">
                  <div className="flex items-center gap-1.5">
                    <span>Monument Name</span>
                    <ArrowUpDown className="w-3 h-3 text-amber-400" />
                  </div>
                </th>
                <th onClick={() => toggleSort("category")} className="cursor-pointer">
                  <div className="flex items-center gap-1.5">
                    <span>Category</span>
                    <ArrowUpDown className="w-3 h-3 text-amber-400" />
                  </div>
                </th>
                <th onClick={() => toggleSort("state")} className="cursor-pointer">
                  <div className="flex items-center gap-1.5">
                    <span>State / District</span>
                    <ArrowUpDown className="w-3 h-3 text-amber-400" />
                  </div>
                </th>
                <th>Period / Era</th>
                <th>Coordinates</th>
                <th>Status</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredSites.map((site) => {
                const badge = getCategoryBadge(site.category);
                const hasCoords = site.latitude != null && site.longitude != null;
                return (
                  <tr key={site.id} className="hover:bg-amber-400/5 transition-colors">
                    <td className="font-semibold text-white">
                      <div className="flex items-center gap-2">
                        <Landmark className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                        <span>{site.name}</span>
                      </div>
                    </td>
                    <td>
                      <span
                        className="category-badge-chip"
                        style={{
                          backgroundColor: badge.bg,
                          color: badge.text,
                          borderColor: badge.border,
                        }}
                      >
                        {site.category || "Monument"}
                      </span>
                    </td>
                    <td className="text-gray-300">
                      {site.state ? `${site.district ? `${site.district}, ` : ""}${site.state}` : "—"}
                    </td>
                    <td className="text-gray-300">{site.period || "—"}</td>
                    <td className="text-xs text-gray-400 font-mono">
                      {hasCoords ? `${site.latitude!.toFixed(4)}, ${site.longitude!.toFixed(4)}` : "Pending"}
                    </td>
                    <td>
                      <span className="verified-badge-chip">
                        <ShieldCheck className="w-3 h-3 text-emerald-400 inline mr-1" />
                        Verified
                      </span>
                    </td>
                    <td className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          className="table-action-btn"
                          onClick={() => onSelectSiteOnMap(site)}
                          title="View on Map"
                        >
                          <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                        </button>
                        <button
                          className="table-action-btn primary"
                          onClick={() => onOpenSiteDossier(site)}
                          title="Open Dossier"
                        >
                          <Eye className="w-3.5 h-3.5 text-amber-400" />
                          <span className="text-xs ml-1">Inspect</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default HeritageExplorerView;
