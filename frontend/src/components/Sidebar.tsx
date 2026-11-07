import React, { useState } from "react";
import {
  LayoutDashboard,
  Compass,
  MapPin,
  Network,
  Bot,
  Box,
  ShieldCheck,
  BarChart3,
  Database,
  Settings,
  ChevronLeft,
  ChevronRight,
  X,
} from "lucide-react";

export type NavTab =
  | "dashboard"
  | "explorer"
  | "map"
  | "graph"
  | "assistant"
  | "3d"
  | "coverage"
  | "analytics"
  | "management"
  | "settings";

interface SidebarProps {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
}

interface NavItemConfig {
  id: NavTab;
  label: string;
  badge?: string;
  icon: React.ComponentType<{ className?: string }>;
}

const navItems: NavItemConfig[] = [
  { id: "dashboard", label: "Command Centre", icon: LayoutDashboard },
  { id: "explorer", label: "Heritage Explorer", badge: "22", icon: Compass },
  { id: "map", label: "India Heritage Map", icon: MapPin },
  { id: "graph", label: "Knowledge Graph", badge: "44", icon: Network },
  { id: "assistant", label: "AI Intelligence", badge: "RAG", icon: Bot },
  { id: "3d", label: "3D Exploration", icon: Box },
  { id: "coverage", label: "National Coverage", badge: "ASI", icon: ShieldCheck },
  { id: "analytics", label: "Heritage Analytics", icon: BarChart3 },
  { id: "management", label: "Preservation Mgmt", icon: Database },
  { id: "settings", label: "Platform Settings", icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onTabChange,
  isOpenMobile,
  onCloseMobile,
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpenMobile && (
        <div
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm lg:hidden"
          onClick={onCloseMobile}
        />
      )}

      <aside
        className={`sidebar ${
          isOpenMobile ? "open" : ""
        } ${isCollapsed ? "collapsed" : ""}`}
      >
        {/* Brand Header */}
        <div className="sidebar-brand">
          <div className="brand-logo-wrapper">
            <svg
              className="brand-temple-icon"
              viewBox="0 0 48 48"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path d="M24 4L28 12H20L24 4Z" fill="url(#goldGrad)" />
              <path d="M17 12H31L33 18H15L17 12Z" fill="url(#goldGrad)" />
              <path d="M12 18H36L38 26H10L12 18Z" fill="url(#goldGrad)" />
              <path d="M8 26H40V40H8V26Z" fill="url(#goldGrad)" opacity="0.95" />
              {/* Sanctum Door */}
              <path
                d="M21 40V30C21 28.3431 22.3431 27 24 27C25.6569 27 27 28.3431 27 30V40H21Z"
                fill="#0a0f18"
              />
              {/* Pillars */}
              <line x1="13" y1="26" x2="13" y2="40" stroke="#0a0f18" strokeWidth="1.5" />
              <line x1="17" y1="26" x2="17" y2="40" stroke="#0a0f18" strokeWidth="1.5" />
              <line x1="31" y1="26" x2="31" y2="40" stroke="#0a0f18" strokeWidth="1.5" />
              <line x1="35" y1="26" x2="35" y2="40" stroke="#0a0f18" strokeWidth="1.5" />
              {/* Base */}
              <rect x="6" y="40" width="36" height="4" rx="1" fill="url(#goldGrad)" />
              {/* Kalasha finial tip */}
              <circle cx="24" cy="4" r="2" fill="#FFE082" />
              <defs>
                <linearGradient
                  id="goldGrad"
                  x1="8"
                  y1="4"
                  x2="40"
                  y2="44"
                  gradientUnits="userSpaceOnUse"
                >
                  <stop stopColor="#FFE082" />
                  <stop offset="0.5" stopColor="#D9A441" />
                  <stop offset="1" stopColor="#9E6E1D" />
                </linearGradient>
              </defs>
            </svg>
          </div>

          {!isCollapsed && (
            <div className="brand-text">
              <h1 className="brand-title">3D BHARAT</h1>
              <p className="brand-tagline">National Heritage Intelligence</p>
            </div>
          )}

          {isOpenMobile && (
            <button
              className="sidebar-close-btn lg:hidden"
              onClick={onCloseMobile}
              aria-label="Close sidebar"
            >
              <X className="w-5 h-5 text-gray-400 hover:text-white" />
            </button>
          )}
        </div>

        {/* Navigation Menu */}
        <nav className="sidebar-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  onTabChange(item.id);
                  if (isOpenMobile) onCloseMobile();
                }}
                className={`nav-item ${isActive ? "active" : ""}`}
                title={isCollapsed ? item.label : undefined}
              >
                <span className="nav-icon-wrapper">
                  <Icon className="nav-icon" />
                </span>
                {!isCollapsed && (
                  <>
                    <span className="nav-label">{item.label}</span>
                    {item.badge && (
                      <span className="nav-item-badge">{item.badge}</span>
                    )}
                  </>
                )}
                {isActive && <span className="active-glow-pill" />}
              </button>
            );
          })}
        </nav>

        {/* Collapse / Expand Toggle Button for Desktop */}
        <div className="sidebar-collapse-container hidden lg:flex">
          <button
            className="sidebar-toggle-btn"
            onClick={() => setIsCollapsed(!isCollapsed)}
            title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          >
            {isCollapsed ? (
              <ChevronRight className="w-4 h-4 text-amber-400" />
            ) : (
              <>
                <ChevronLeft className="w-4 h-4 text-gray-400 group-hover:text-amber-400" />
                <span className="text-xs text-gray-400 group-hover:text-white">Collapse Menu</span>
              </>
            )}
          </button>
        </div>

        {/* Sidebar Footer Artwork & Slogan */}
        {!isCollapsed && (
          <div className="sidebar-footer">
            <div className="temple-artwork-container">
              <svg
                className="temple-carving-svg"
                viewBox="0 0 200 110"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M100 8 L104 22 L112 36 L124 55 L144 80 L165 94 L35 94 L56 80 L76 55 L88 36 L96 22 Z"
                  fill="url(#carvingStone)"
                  opacity="0.85"
                />
                <path
                  d="M100 8 V94 M88 36 H112 M76 55 H124 M56 80 H144"
                  stroke="#D9A441"
                  strokeWidth="0.8"
                  strokeDasharray="2 2"
                  opacity="0.6"
                />
                <rect x="25" y="94" width="150" height="8" rx="2" fill="url(#carvingStone)" />
                <circle cx="100" cy="8" r="3" fill="#FFE082" />
                <defs>
                  <linearGradient
                    id="carvingStone"
                    x1="100"
                    y1="8"
                    x2="100"
                    y2="102"
                    gradientUnits="userSpaceOnUse"
                  >
                    <stop stopColor="#3d2c19" />
                    <stop offset="0.6" stopColor="#22180d" />
                    <stop offset="1" stopColor="#120c06" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <p className="heritage-quote">
              “Our Heritage...
              <br />
              Our Pride... Our Bharat...”
            </p>
            <div className="tiranga-strip">
              <span className="tiranga-saffron" />
              <span className="tiranga-white" />
              <span className="tiranga-green" />
            </div>
          </div>
        )}
      </aside>
    </>
  );
};

export default Sidebar;
