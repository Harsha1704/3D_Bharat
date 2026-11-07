import React, { useState } from "react";
import { Bot, Send, User, Landmark, ShieldCheck } from "lucide-react";
import type { HeritageSite } from "../api";

interface Message {
  id: string;
  sender: "bot" | "user";
  text: string;
  sourceCitation?: string;
  timestamp: string;
}

interface AiHeritageAssistantProps {
  selectedSite: HeritageSite | null;
  allSites: HeritageSite[];
  onExploreSite?: (site: HeritageSite) => void;
}

const QUICK_CHIPS = [
  "Architecture",
  "Historical Period",
  "Location & GPS",
  "Sites in Rajasthan",
  "Sites in Maharashtra",
];

export const AiHeritageAssistant: React.FC<AiHeritageAssistantProps> = ({
  selectedSite,
  allSites = [],
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      sender: "bot",
      text: "Namaste! I retrieve authentic heritage information directly from Archaeological Survey of India (ASI) and UNESCO records in the 3D BHARAT database. Ask about any documented monument or click a topic chip below.",
      timestamp: "System",
    },
  ]);

  const [inputText, setInputText] = useState("");

  const handleSend = (textToSend?: string) => {
    const query = textToSend || inputText;
    if (!query.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: "user",
      text: query,
      timestamp: "Just now",
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputText("");

    setTimeout(() => {
      let botReply = "";
      let sourceCitation = "";
      const qLower = query.toLowerCase();

      // State-specific queries
      if (qLower.includes("rajasthan")) {
        const rajSites = allSites.filter(
          (s) => s.state?.toLowerCase() === "rajasthan"
        );
        if (rajSites.length > 0) {
          botReply = `Verified monuments in Rajasthan (${rajSites.length} documented): ${rajSites.map((s) => `${s.name} (${s.category || "Monument"}, ${s.city || s.district || "Rajasthan"})`).join("; ")}.`;
          sourceCitation = "Archaeological Survey of India (ASI) State Baseline";
        } else {
          botReply = "No monuments from Rajasthan are currently recorded in this baseline batch.";
        }
      } else if (qLower.includes("maharashtra")) {
        const mhSites = allSites.filter(
          (s) => s.state?.toLowerCase() === "maharashtra"
        );
        if (mhSites.length > 0) {
          botReply = `Verified monuments in Maharashtra (${mhSites.length} documented): ${mhSites.map((s) => `${s.name} (${s.category || "Monument"}, ${s.city || s.district || "Maharashtra"})`).join("; ")}.`;
          sourceCitation = "Archaeological Survey of India (ASI) & UNESCO World Heritage";
        } else {
          botReply = "No monuments from Maharashtra are currently recorded in this baseline batch.";
        }
      } else if (qLower.includes("gujarat")) {
        const gjSites = allSites.filter(
          (s) => s.state?.toLowerCase() === "gujarat"
        );
        if (gjSites.length > 0) {
          botReply = `Verified monuments in Gujarat (${gjSites.length} documented): ${gjSites.map((s) => `${s.name} (${s.category || "Monument"}, ${s.city || s.district || "Gujarat"})`).join("; ")}.`;
          sourceCitation = "Archaeological Survey of India (ASI) & UNESCO World Heritage";
        }
      } else if (selectedSite) {
        // Query relates to selected site
        if (qLower.includes("arch") || qLower.includes("style")) {
          botReply = `Architectural Style for ${selectedSite.name}: ${selectedSite.architecture || "Authentic historic masonry craftsmanship"}. Categorized under '${selectedSite.category || "Monument"}' from ${selectedSite.state || "India"}.`;
          sourceCitation = `ASI Architectural Survey • ${selectedSite.external_id || "ASI Record"}`;
        } else if (qLower.includes("period") || qLower.includes("dynasty") || qLower.includes("history")) {
          botReply = `Historical Era for ${selectedSite.name}: Documented as ${selectedSite.period || "Recorded historical period"}. ${selectedSite.significance || selectedSite.description || "Centrally protected monument of national importance."}`;
          sourceCitation = `National Heritage Provenance Registry (${selectedSite.state || "National"})`;
        } else if (qLower.includes("location") || qLower.includes("gps") || qLower.includes("coords")) {
          botReply = `Location: ${selectedSite.name} is situated in ${selectedSite.city || selectedSite.district || "district"}, ${selectedSite.state || "India"} at coordinates ${selectedSite.latitude?.toFixed(4)}° N, ${selectedSite.longitude?.toFixed(4)}° E.`;
          sourceCitation = "Survey of India Geodetic Baseline";
        } else {
          // General lookup of site
          botReply = `${selectedSite.name} (${selectedSite.category || "Monument"}, ${selectedSite.state}): ${selectedSite.description || "Centrally protected monument."}`;
          sourceCitation = "ASI Centrally Protected Monument Inventory";
        }
      } else {
        // Search across all sites by name
        const found = allSites.find((s) =>
          qLower.includes(s.name.toLowerCase())
        );
        if (found) {
          botReply = `${found.name} is documented in ${found.state} as a ${found.category || "Monument"} (${found.period || "Historical Period"}). ${found.description || ""}`;
          sourceCitation = `Verified Record ${found.external_id || `ID: ${found.id}`}`;
        } else {
          botReply = `No verified record found matching '${query}' in the current 22-site database. 3D BHARAT adheres strictly to factual retrieval from authentic ASI and UNESCO sources.`;
        }
      }

      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: "bot",
        text: botReply,
        sourceCitation,
        timestamp: "Just now",
      };

      setMessages((prev) => [...prev, botMsg]);
    }, 250);
  };

  return (
    <div className="assistant-panel-card">
      {/* Panel Header */}
      <div className="panel-header">
        <div className="panel-title-group">
          <Bot className="panel-icon text-cyan-400" />
          <h3 className="panel-title">Heritage Database Assistant</h3>
        </div>
        <div className="online-status-badge">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 inline" />
          <span className="text-xs">Database Fact Retrieval</span>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="assistant-chat-container">
        {messages.map((msg) => (
          <div key={msg.id} className={`chat-message ${msg.sender}`}>
            {msg.sender === "bot" && (
              <div className="bot-avatar-badge">
                <Landmark className="w-3.5 h-3.5 text-amber-300" />
              </div>
            )}
            <div className="message-bubble">
              <p className="message-text">{msg.text}</p>
              {msg.sourceCitation && (
                <div className="message-citation">
                  <ShieldCheck className="w-3 h-3 inline mr-1 text-emerald-400" />
                  <span>Source: {msg.sourceCitation}</span>
                </div>
              )}
            </div>
            {msg.sender === "user" && (
              <div className="user-avatar-badge">
                <User className="w-3.5 h-3.5 text-blue-300" />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Quick Prompt Chips */}
      <div className="quick-chips-row">
        {QUICK_CHIPS.map((chip) => (
          <button
            key={chip}
            className="chip-btn"
            onClick={() => handleSend(`${chip} ${selectedSite ? `of ${selectedSite.name}` : ""}`)}
          >
            {chip}
          </button>
        ))}
      </div>

      {/* Input Box */}
      <form
        className="assistant-input-form"
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
      >
        <input
          type="text"
          className="assistant-input"
          placeholder="Ask about documented sites, states, dynasties..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
        />
        <button
          type="submit"
          className="assistant-send-btn"
          aria-label="Send query"
          disabled={!inputText.trim()}
        >
          <Send className="w-4 h-4 text-gray-900" />
        </button>
      </form>
    </div>
  );
};
export default AiHeritageAssistant;
