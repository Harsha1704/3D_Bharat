import React, { useState, useEffect, useRef } from "react";
import {
  Bot,
  Send,
  User,
  Landmark,
  ShieldCheck,
  Sparkles,
  ExternalLink,
  BookOpen,
  Info,
  Loader2,
  X,
  MapPin,
  Calendar,
  MessageSquare,
} from "lucide-react";
import {
  chatWithHeritageAI,
  getAIStatus,
  type HeritageSite,
  type AICitation,
  type AIStatusResponse,
} from "../api";

interface ChatMessage {
  id: string;
  sender: "bot" | "user";
  text: string;
  citations?: AICitation[];
  evidenceStatus?: string;
  evidenceSummary?: string;
  timestamp: string;
}

interface AiHeritageAssistantProps {
  selectedSite: HeritageSite | null;
  allSites: HeritageSite[];
  onExploreSite?: (site: HeritageSite) => void;
  isExpanded?: boolean;
}

const RESEARCH_TOPICS = [
  "Significance of Brihadisvara Temple and Chola evidence",
  "Which dynasty and architectural style built Taj Mahal?",
  "Dravidian architectural elements in South Indian temples",
  "Monastic traditions preserved at Ajanta Caves",
  "Vijayanagara stone engineering at Hampi",
  "Hydraulic engineering at Rani-ki-Vav stepwell",
  "Buddhist philosophy reflected in Sanchi Stupa 1",
  "Kailasa Temple monolithic excavation technique",
];

export const AiHeritageAssistant: React.FC<AiHeritageAssistantProps> = ({
  selectedSite,
  allSites = [],
  onExploreSite,
  isExpanded = false,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      sender: "bot",
      text: "Namaste! I am your AI Heritage Intelligence Assistant. I provide truthful, evidence-grounded research on Indian monuments, dynasties, and architecture backed directly by Archaeological Survey of India (ASI) and UNESCO records.",
      timestamp: "System",
      evidenceStatus: "DOCUMENTED",
    },
  ]);

  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const [researchMode, setResearchMode] = useState(false);
  const [aiStatus, setAiStatus] = useState<AIStatusResponse | null>(null);
  const [selectedCitation, setSelectedCitation] = useState<AICitation | null>(null);
  const [activeSiteContext, setActiveSiteContext] = useState<HeritageSite | null>(selectedSite);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Sync prop changes
  useEffect(() => {
    if (selectedSite) setActiveSiteContext(selectedSite);
  }, [selectedSite]);

  // Fetch AI service capability status
  useEffect(() => {
    let mounted = true;
    getAIStatus()
      .then((status) => {
        if (mounted) setAiStatus(status);
      })
      .catch(() => {});
    return () => {
      mounted = false;
    };
  }, []);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Handle message send
  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || inputText;
    if (!textToSend.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: "user",
      text: textToSend.trim(),
      timestamp: "Just now",
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText("");
    setLoading(true);

    try {
      const response = await chatWithHeritageAI({
        message: textToSend.trim(),
        selected_site_id: activeSiteContext?.id,
        research_mode: researchMode,
      });

      const botMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: "bot",
        text: response.answer,
        citations: response.citations,
        evidenceStatus: response.evidence_status,
        evidenceSummary: response.retrieved_evidence_summary,
        timestamp: "Evidence Grounded",
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: "bot",
        text: `Unable to complete research query: ${err.message || "Backend retrieval service offline"}. Please verify connection to the 3D Bharat backend API.`,
        timestamp: "Error",
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  // If expanded full-screen research mode
  if (isExpanded) {
    return (
      <div className="ai-research-workspace-layout">
        {/* Left Column: Research Topics & Monument Context Selector */}
        <aside className="research-sidebar-left">
          <div className="research-sidebar-header">
            <MessageSquare className="w-4 h-4 text-amber-400" />
            <h4 className="text-xs uppercase tracking-wider text-white font-bold">
              Research Prompts
            </h4>
          </div>

          <div className="research-topics-list">
            {RESEARCH_TOPICS.map((topic, i) => (
              <button
                key={i}
                className="topic-pill-btn"
                onClick={() => handleSend(topic)}
                disabled={loading}
              >
                <Sparkles className="w-3 h-3 text-cyan-400 shrink-0" />
                <span>{topic}</span>
              </button>
            ))}
          </div>

          <div className="research-context-selector-box mt-6">
            <span className="text-xs font-semibold text-gray-300 block mb-2">
              Filter by Active Monument Context
            </span>
            <select
              className="context-monument-select"
              value={activeSiteContext?.id || ""}
              onChange={(e) => {
                const siteId = Number(e.target.value);
                const matched = allSites.find((s) => s.id === siteId) || null;
                setActiveSiteContext(matched);
              }}
            >
              <option value="">All National Monuments (Pan-India)</option>
              {allSites.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.state})
                </option>
              ))}
            </select>
          </div>

          <div className="honest-corpus-status-box mt-6">
            <Info className="w-4 h-4 text-cyan-400 shrink-0" />
            <div className="text-[11px] text-gray-400 leading-snug">
              <strong className="text-gray-200 block mb-0.5">Corpus Integrity</strong>
              0 Full-Text Documents in Vector Chunk Index. Live retrieval queries the 22 verified database monuments & 44 graph entities directly.
            </div>
          </div>
        </aside>

        {/* Center Column: Spacious Chat Interface */}
        <main className="research-chat-centre">
          <div className="research-chat-header">
            <div className="flex items-center gap-2">
              <Bot className="w-5 h-5 text-cyan-400" />
              <div>
                <h3 className="text-base font-bold text-white">AI Heritage Intelligence</h3>
                <span className="text-xs text-gray-400">
                  Scholarly Research Environment • Traceable Citations
                </span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                className={`btn-research-mode ${researchMode ? "active" : ""}`}
                onClick={() => setResearchMode(!researchMode)}
              >
                <Sparkles className="w-3.5 h-3.5 mr-1" />
                <span>Deep Research</span>
              </button>
              <span className="live-status-pill">
                <span className="live-pulse-dot" />
                <span>{aiStatus?.provider_configured ? "Model Ready" : "Grounded Retrieval"}</span>
              </span>
            </div>
          </div>

          {/* Messages */}
          <div className="research-messages-area">
            {messages.map((msg) => (
              <div key={msg.id} className={`chat-message-row ${msg.sender}`}>
                {msg.sender === "bot" && (
                  <div className="message-avatar bot">
                    <Landmark className="w-4 h-4 text-amber-400" />
                  </div>
                )}
                {msg.sender === "user" && (
                  <div className="message-avatar user">
                    <User className="w-4 h-4 text-cyan-400" />
                  </div>
                )}

                <div className="message-card-bubble">
                  <p className="message-prose">{msg.text}</p>

                  {/* Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="citations-tray">
                      <span className="citations-title">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 mr-1 inline" />
                        Retrieved Evidence Sources:
                      </span>
                      <div className="citations-list-row">
                        {msg.citations.map((c) => (
                          <button
                            key={c.citation_id}
                            className="citation-chip-btn"
                            onClick={() => setSelectedCitation(c)}
                          >
                            <span className="citation-id-num">{c.citation_id}</span>
                            <span className="citation-title-text">{c.source_title}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="message-meta-footer">
                    {msg.evidenceStatus && (
                      <span className={`evidence-badge ${msg.evidenceStatus.toLowerCase()}`}>
                        {msg.evidenceStatus}
                      </span>
                    )}
                    <span className="time-tag">{msg.timestamp}</span>
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Box */}
          <form
            className="research-chat-input-bar"
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
          >
            <input
              type="text"
              className="research-input-field"
              placeholder={
                activeSiteContext
                  ? `Ask about ${activeSiteContext.name}, dynastic period, or architectural significance...`
                  : "Ask about Indian monuments, dynasties, architectural styles, or inscriptions..."
              }
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              disabled={loading}
            />
            <button
              type="submit"
              className="research-submit-btn"
              disabled={!inputText.trim() || loading}
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin text-gray-900" />
              ) : (
                <Send className="w-4 h-4 text-gray-900" />
              )}
            </button>
          </form>
        </main>

        {/* Right Column: Selected Monument Context & Citation Viewer */}
        <aside className="research-sidebar-right hidden xl:flex">
          {activeSiteContext ? (
            <div className="context-monument-card">
              <div className="context-card-header">
                <span className="text-xs uppercase tracking-wider text-amber-400 font-bold">
                  Active Context
                </span>
                <span className="context-category">{activeSiteContext.category || "Monument"}</span>
              </div>

              <h4 className="context-name">{activeSiteContext.name}</h4>
              <div className="context-location">
                <MapPin className="w-3.5 h-3.5 text-gray-400 mr-1" />
                <span>{activeSiteContext.city || activeSiteContext.district}, {activeSiteContext.state}</span>
              </div>

              <p className="context-description">
                {activeSiteContext.description || "Historical monument documented in the central database."}
              </p>

              {activeSiteContext.period && (
                <div className="context-era">
                  <Calendar className="w-3.5 h-3.5 text-gray-400 mr-1.5" />
                  <span>{activeSiteContext.period}</span>
                </div>
              )}

              {onExploreSite && (
                <button
                  className="btn-view-dossier-small mt-4"
                  onClick={() => onExploreSite(activeSiteContext)}
                >
                  Inspect Complete Dossier
                </button>
              )}
            </div>
          ) : (
            <div className="empty-context-box">
              <Landmark className="w-8 h-8 text-amber-400/30 mb-2" />
              <span className="text-xs text-gray-400">Pan-India General Retrieval Active</span>
              <span className="text-[11px] text-gray-500 mt-1">Select a monument from the left to narrow context.</span>
            </div>
          )}
        </aside>

        {/* Citation Popover Modal */}
        {selectedCitation && (
          <div className="citation-modal-backdrop" onClick={() => setSelectedCitation(null)}>
            <div className="citation-modal-card" onClick={(e) => e.stopPropagation()}>
              <div className="citation-modal-header">
                <div className="flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-amber-400" />
                  <h4 className="citation-modal-title">
                    Citation {selectedCitation.citation_id}: {selectedCitation.source_title}
                  </h4>
                </div>
                <button className="citation-close-btn" onClick={() => setSelectedCitation(null)}>
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="citation-modal-body">
                <div className="citation-meta-item">
                  <span className="meta-label">Institution:</span>
                  <span className="meta-val">
                    {selectedCitation.institution || "Archaeological Survey of India (ASI)"}
                  </span>
                </div>
                <div className="citation-excerpt-box">
                  <span className="meta-label block mb-1">Archival Text Excerpt:</span>
                  <p className="excerpt-text">{selectedCitation.relevant_excerpt}</p>
                </div>
                {selectedCitation.source_url && (
                  <a
                    href={selectedCitation.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="citation-external-link"
                  >
                    Open Archival Source <ExternalLink className="w-3.5 h-3.5 ml-1" />
                  </a>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Compact mode for dashboard
  return (
    <div className="assistant-panel-card">
      <div className="panel-header">
        <div className="panel-title-group">
          <Bot className="panel-icon text-cyan-400" />
          <div>
            <h3 className="panel-title">AI Heritage Assistant</h3>
            <span className="text-xs text-gray-400 block">
              Grounded RAG & Cultural Knowledge Graph
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div
            className={`ai-status-indicator ${
              aiStatus?.provider_configured ? "status-online" : "status-fallback"
            }`}
          >
            <span className="status-dot"></span>
            <span className="status-text">
              {aiStatus?.provider_configured ? "AI Online" : "Grounded Archive"}
            </span>
          </div>
        </div>
      </div>

      {activeSiteContext && (
        <div className="assistant-context-banner">
          <Landmark className="w-3.5 h-3.5 text-amber-400" />
          <span className="context-text">
            Active Context: <strong>{activeSiteContext.name}</strong> ({activeSiteContext.state})
          </span>
        </div>
      )}

      <div className="assistant-chat-container">
        {messages.map((msg) => (
          <div key={msg.id} className={`chat-message ${msg.sender}`}>
            {msg.sender === "bot" && (
              <div className="bot-avatar-badge">
                <Landmark className="w-4 h-4 text-amber-300" />
              </div>
            )}
            <div className="message-bubble">
              <p className="message-text">{msg.text}</p>
              {msg.citations && msg.citations.length > 0 && (
                <div className="message-citations-container">
                  <div className="citations-header">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 mr-1" />
                    <span>Verified Citations ({msg.citations.length}):</span>
                  </div>
                  <div className="citations-pills-row">
                    {msg.citations.map((c) => (
                      <button
                        key={c.citation_id}
                        type="button"
                        className="citation-pill"
                        onClick={() => setSelectedCitation(c)}
                      >
                        <span className="citation-num">{c.citation_id}</span>
                        <span className="citation-name">{c.source_title}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

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
          placeholder="Ask about documented monuments, dynasties, or architecture..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          disabled={loading}
        />
        <button
          type="submit"
          className="assistant-send-btn"
          disabled={!inputText.trim() || loading}
        >
          {loading ? (
            <Loader2 className="w-4 h-4 text-gray-900 animate-spin" />
          ) : (
            <Send className="w-4 h-4 text-gray-900" />
          )}
        </button>
      </form>
    </div>
  );
};

export default AiHeritageAssistant;
