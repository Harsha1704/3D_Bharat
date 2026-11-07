import React, { useState, useRef, useEffect } from "react";
import { Search, Bell, Menu, X, Landmark, MapPin, Sparkles } from "lucide-react";
import type { HeritageSite } from "../api";

interface HeaderProps {
  onSearchSelect: (site: HeritageSite) => void;
  sites: HeritageSite[];
  onOpenMobileMenu: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  onSearchSelect,
  sites,
  onOpenMobileMenu,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);
  const notifRef = useRef<HTMLDivElement>(null);

  // Filter sites live based on search term
  const filteredSuggestions = searchTerm.trim()
    ? sites
        .filter((site) => {
          const term = searchTerm.toLowerCase();
          return (
            site.name.toLowerCase().includes(term) ||
            (site.state && site.state.toLowerCase().includes(term)) ||
            (site.category && site.category.toLowerCase().includes(term)) ||
            (site.district && site.district.toLowerCase().includes(term))
          );
        })
        .slice(0, 6)
    : [];

  // Close search/notif when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        searchRef.current &&
        !searchRef.current.contains(event.target as Node)
      ) {
        setIsSearchOpen(false);
      }
      if (
        notifRef.current &&
        !notifRef.current.contains(event.target as Node)
      ) {
        setShowNotifications(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className="dashboard-header">
      {/* Left: Mobile Toggle & Tiranga Greeting */}
      <div className="header-left">
        <button
          className="mobile-menu-btn lg:hidden"
          onClick={onOpenMobileMenu}
          aria-label="Open menu"
        >
          <Menu className="w-6 h-6 text-amber-400" />
        </button>

        <div className="greeting-container">
          <div className="tiranga-ribbon-badge">
            <svg
              className="tiranga-ribbon-svg"
              viewBox="0 0 44 28"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              {/* Saffron Wave */}
              <path
                d="M2 7 C12 2, 24 12, 42 6"
                stroke="#FF9933"
                strokeWidth="4"
                strokeLinecap="round"
              />
              {/* White Wave */}
              <path
                d="M2 14 C12 9, 24 19, 42 13"
                stroke="#FFFFFF"
                strokeWidth="4"
                strokeLinecap="round"
              />
              {/* Ashoka Chakra in miniature center */}
              <circle cx="22" cy="14" r="2.5" stroke="#000080" strokeWidth="0.8" fill="none" />
              {/* Green Wave */}
              <path
                d="M2 21 C12 16, 24 26, 42 20"
                stroke="#138808"
                strokeWidth="4"
                strokeLinecap="round"
              />
            </svg>
          </div>

          <div className="greeting-text">
            <h2 className="welcome-title">
              Welcome back, <span className="user-name">Harsha!</span>
            </h2>
            <p className="welcome-subtitle">
              Discover the timeless heritage of India with AI-powered insights
            </p>
          </div>
        </div>
      </div>

      {/* Center: Search Bar */}
      <div className="header-center" ref={searchRef}>
        <div className="search-bar-wrapper">
          <Search className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search heritage sites, dynasties, monuments..."
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
            >
              <X className="w-4 h-4 text-gray-400 hover:text-white" />
            </button>
          )}
        </div>

        {/* Live Search Suggestions Dropdown */}
        {isSearchOpen && filteredSuggestions.length > 0 && (
          <div className="search-dropdown">
            <div className="search-dropdown-header">
              <span>Matching Heritage Monuments</span>
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
                    {site.city || site.district || "India"}, {site.state}
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

      {/* Right: Silhouette Artwork, Notification Bell, User Avatar */}
      <div className="header-right">
        {/* Taj Mahal Silhouette Watermark / Artwork */}
        <div className="ambient-monument-silhouette" title="National Heritage Intelligence Platform">
          <svg
            className="taj-silhouette-svg"
            viewBox="0 0 160 55"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            {/* Center Dome */}
            <path
              d="M80 6 C76 16, 70 20, 70 32 L90 32 C90 20, 84 16, 80 6 Z"
              fill="#D9A441"
              opacity="0.3"
            />
            {/* Finial */}
            <line x1="80" y1="2" x2="80" y2="6" stroke="#FFC857" strokeWidth="1.5" opacity="0.6" />
            {/* Center Arch Body */}
            <rect x="66" y="32" width="28" height="20" rx="1" fill="#D9A441" opacity="0.25" />
            <path d="M74 52 V40 C74 37, 86 37, 86 40 V52 Z" fill="#070B12" />
            {/* Side Chhatris */}
            <path d="M56 22 L62 26 V32 H50 V26 Z" fill="#D9A441" opacity="0.25" />
            <path d="M104 22 L110 26 V32 H98 V26 Z" fill="#D9A441" opacity="0.25" />
            {/* Minarets */}
            <rect x="36" y="16" width="4" height="36" fill="#D9A441" opacity="0.2" />
            <circle cx="38" cy="15" r="3" fill="#D9A441" opacity="0.3" />
            <rect x="120" y="16" width="4" height="36" fill="#D9A441" opacity="0.2" />
            <circle cx="122" cy="15" r="3" fill="#D9A441" opacity="0.3" />
            {/* Base Plinth */}
            <rect x="25" y="52" width="110" height="3" fill="#D9A441" opacity="0.35" />
          </svg>
        </div>

        {/* Notifications */}
        <div className="notification-wrapper" ref={notifRef}>
          <button
            className="notification-btn"
            onClick={() => setShowNotifications(!showNotifications)}
            aria-label="View notifications"
          >
            <Bell className="w-5 h-5 text-gray-300 hover:text-amber-400 transition-colors" />
            <span className="notification-badge">1</span>
          </button>

          {showNotifications && (
            <div className="notification-dropdown">
              <div className="notif-header">
                <span>System Notifications</span>
                <span className="notif-unread-count">1 Unread</span>
              </div>
              <div className="notif-item unread">
                <div className="notif-icon">
                  <Sparkles className="w-4 h-4 text-amber-400" />
                </div>
                <div className="notif-content">
                  <p className="notif-title">Phase 7 Live Integration Ready</p>
                  <p className="notif-time">Verified baseline with 22 heritage monuments & 8 connections loaded.</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* User Profile Pill */}
        <div className="user-profile-pill">
          <div className="user-avatar-circle">
            <span className="avatar-initial">H</span>
          </div>
        </div>
      </div>
    </header>
  );
};
export default Header;
