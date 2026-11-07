import React, { useState, useRef, useEffect } from "react";
import { useLocation, Link } from "react-router-dom";
import {
  Search,
  Bell,
  Menu,
  X,
  Landmark,
  MapPin,
  Sparkles,
  ShieldCheck,
  ChevronRight,
} from "lucide-react";
import type { HeritageSite } from "../api";

interface HeaderProps {
  onSearchSelect: (site: HeritageSite) => void;
  sites: HeritageSite[];
  onOpenMobileMenu: () => void;
  totalSites?: number;
  distinctStatesCount?: number;
}

const ROUTE_PAGE_TITLES: Record<string, string> = {
  "/": "National Command Centre",
  "/dashboard": "National Command Centre",
  "/explorer": "Heritage Explorer",
  "/map": "All India Heritage Map",
  "/graph": "Cultural Knowledge Graph",
  "/assistant": "AI Heritage Intelligence",
  "/3d": "3D Digital Preservation",
  "/coverage": "National Coverage & ASI Audit",
  "/analytics": "Heritage Analytics",
  "/management": "Preservation Management",
  "/settings": "Platform Settings",
};

export const Header: React.FC<HeaderProps> = ({
  onSearchSelect,
  sites,
  onOpenMobileMenu,
  totalSites = 22,
  distinctStatesCount = 12,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);
  const notifRef = useRef<HTMLDivElement>(null);
  const location = useLocation();

  // Filter sites live based on search term
  const filteredSuggestions = searchTerm.trim()
    ? sites
        .filter((site) => {
          const term = searchTerm.toLowerCase();
          return (
            site.name.toLowerCase().includes(term) ||
            (site.state && site.state.toLowerCase().includes(term)) ||
            (site.category && site.category.toLowerCase().includes(term)) ||
            (site.district && site.district.toLowerCase().includes(term)) ||
            (site.period && site.period.toLowerCase().includes(term))
          );
        })
        .slice(0, 7)
    : [];

  // Close search/notif when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsSearchOpen(false);
      }
      if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const pageTitle = ROUTE_PAGE_TITLES[location.pathname] || "Heritage Intelligence";

  return (
    <header className="dashboard-header">
      {/* Left: Mobile Toggle & Breadcrumbs */}
      <div className="header-left">
        <button
          className="mobile-menu-btn lg:hidden"
          onClick={onOpenMobileMenu}
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5 text-amber-400" />
        </button>

        {/* Command Centre Breadcrumbs */}
        <div className="header-breadcrumbs">
          <Link to="/" className="breadcrumb-brand">
            <span className="brand-dot" />
            <span className="brand-name">3D BHARAT</span>
          </Link>
          <ChevronRight className="w-3.5 h-3.5 text-gray-500" />
          <h2 className="header-page-title">{pageTitle}</h2>
        </div>

        {/* Live Reconciled System Status Pill */}
        <div className="header-status-pill hidden md:flex" title="PostgreSQL 17 Database Connected">
          <span className="status-live-indicator" />
          <span className="status-live-text">
            Live • <strong>{sites.length || totalSites}</strong> Monuments • <strong>{distinctStatesCount}</strong> States • DB Connected
          </span>
        </div>
      </div>

      {/* Center: Global Search Bar */}
      <div className="header-center" ref={searchRef}>
        <div className="search-bar-wrapper">
          <Search className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search monuments, dynasties, UNESCO sites, states..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setIsSearchOpen(true);
            }}
            onFocus={() => setIsSearchOpen(true)}
          />
          {searchTerm && (
            <button
              className="clear-search-btn"
              onClick={() => {
                setSearchTerm("");
                setIsSearchOpen(false);
              }}
              title="Clear search"
            >
              <X className="w-4 h-4 text-gray-400 hover:text-white" />
            </button>
          )}
        </div>

        {/* Live Search Suggestions Dropdown */}
        {isSearchOpen && filteredSuggestions.length > 0 && (
          <div className="search-dropdown">
            <div className="search-dropdown-header">
              <span>National Heritage Catalogue</span>
              <span className="count-pill">{filteredSuggestions.length} found</span>
            </div>
            {filteredSuggestions.map((site) => (
              <div
                key={site.id}
                className="search-item"
                onClick={() => {
                  onSearchSelect(site);
                  setIsSearchOpen(false);
                  setSearchTerm("");
                }}
              >
                <div className="search-item-icon">
                  <Landmark className="w-4 h-4 text-amber-400" />
                </div>
                <div className="search-item-info">
                  <span className="search-item-name">{site.name}</span>
                  <span className="search-item-loc">
                    <MapPin className="w-3 h-3 inline mr-1 text-gray-400" />
                    {site.city || site.district || "India"}
                    {site.state ? `, ${site.state}` : ""}
                  </span>
                </div>
                {site.category && (
                  <span className="search-item-category">{site.category}</span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Right: Taj Mahal Ambient Silhouette, Notifications & Officer Profile */}
      <div className="header-right">
        {/* Taj Mahal Silhouette Watermark / Artwork */}
        <div className="ambient-monument-silhouette" title="National Heritage Intelligence Platform">
          <svg
            className="taj-silhouette-svg"
            viewBox="0 0 160 55"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M80 6 C76 16, 70 20, 70 32 L90 32 C90 20, 84 16, 80 6 Z"
              fill="#D9A441"
              opacity="0.3"
            />
            <line x1="80" y1="2" x2="80" y2="6" stroke="#FFC857" strokeWidth="1.5" opacity="0.6" />
            <rect x="66" y="32" width="28" height="20" rx="1" fill="#D9A441" opacity="0.25" />
            <path d="M74 52 V40 C74 37, 86 37, 86 40 V52 Z" fill="#070B12" />
            <path d="M56 22 L62 26 V32 H50 V26 Z" fill="#D9A441" opacity="0.25" />
            <path d="M104 22 L110 26 V32 H98 V26 Z" fill="#D9A441" opacity="0.25" />
            <rect x="36" y="16" width="4" height="36" fill="#D9A441" opacity="0.2" />
            <circle cx="38" cy="15" r="3" fill="#D9A441" opacity="0.3" />
            <rect x="120" y="16" width="4" height="36" fill="#D9A441" opacity="0.2" />
            <circle cx="122" cy="15" r="3" fill="#D9A441" opacity="0.3" />
            <rect x="25" y="52" width="110" height="3" fill="#D9A441" opacity="0.35" />
          </svg>
        </div>

        {/* Notifications */}
        <div className="notification-wrapper" ref={notifRef}>
          <button
            className="notification-btn"
            onClick={() => setShowNotifications(!showNotifications)}
            aria-label="View system notifications"
            title="System Notifications"
          >
            <Bell className="w-5 h-5 text-gray-300 hover:text-amber-400 transition-colors" />
            <span className="notification-badge">2</span>
          </button>

          {showNotifications && (
            <div className="notification-dropdown">
              <div className="notif-header">
                <span>System Audit Notifications</span>
                <span className="notif-unread-count">2 Active</span>
              </div>
              <div className="notif-item unread">
                <div className="notif-icon">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                </div>
                <div className="notif-content">
                  <p className="notif-title">Command Centre Online</p>
                  <p className="notif-time">
                    Verified baseline of 22 heritage monuments, 44 cultural entities, and 35 relationships.
                  </p>
                </div>
              </div>
              <div className="notif-item unread">
                <div className="notif-icon">
                  <Sparkles className="w-4 h-4 text-cyan-400" />
                </div>
                <div className="notif-content">
                  <p className="notif-title">Phase 9 AI Intelligence Active</p>
                  <p className="notif-time">
                    Evidence-grounded RAG pipeline with verified citations ready.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* User Profile Pill */}
        <Link to="/settings" className="user-profile-pill" title="Platform Settings & Officer Profile">
          <div className="user-avatar-circle">
            <span className="avatar-initial">H</span>
          </div>
          <div className="user-info-text hidden xl:block">
            <span className="user-name-label">Harsha</span>
            <span className="user-role-label">Lead Researcher</span>
          </div>
        </Link>
      </div>
    </header>
  );
};

export default Header;
