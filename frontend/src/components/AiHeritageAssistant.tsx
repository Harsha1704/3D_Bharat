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

const RESEARCH_SUGGESTIONS = [
  "Significance of Brihadisvara Temple and Chola evidence",
  "Which dynasty and architectural style built Taj Mahal?",
  "Dravidian architectural elements in South Indian temples",
  "Monastic traditions preserved at Ajanta Caves",
  "Vijayanagara stone engineering at Hampi",
];

export const AiHeritageAssistant: React.FC<AiHeritageAssistantProps> = ({
  selectedSite,
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

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 1. Fetch AI service capability status
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

  // 2. Auto-scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // 3. Handle message send
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
    if (!queryText) setInputText("");
    setLoading(true);

    try {
      const response = await chatWithHeritageAI({
        message: textToSend.trim(),
        selected_site_id: selectedSite?.id,
        research_mode: researchMode,
      });

      const botMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: "bot",
        text: response.answer,
        citations: response.citations,
        evidenceStatus: response.evidence_status,
        evidenceSummary: response.retrieved_evidence_summary,
        timestamp: "Just now",
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: "bot",
        text: `Unable to retrieve verified heritage records: ${err.message || "Connection failed"}. Please retry.`,
        timestamp: "Error",
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`assistant-panel-card ${isExpanded ? "expanded-assistant" : ""}`}>
      {/* Panel Header */}
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

        {/* Honest Status Badge */}
        <div className="flex items-center gap-3">
          {aiStatus ? (
            <div
              className={`ai-status-indicator ${
                aiStatus.provider_configured ? "status-online" : "status-fallback"
              }`}
              title={
                aiStatus.provider_configured
                  ? `AI Provider: ${aiStatus.provider} (${aiStatus.model})`
                  : "External LLM unconfigured. Grounded factual retrieval active."
              }
            >
              <span className="status-dot"></span>
              <span className="status-text">
                {aiStatus.provider_configured ? "AI Online" : "Grounded Archive"}
              </span>
            </div>
          ) : (
            <span className="text-xs text-gray-500">Checking...</span>
          )}

          {/* Research Mode Switch */}
          <button
            type="button"
            className={`btn-research-mode ${researchMode ? "active" : ""}`}
            onClick={() => setResearchMode(!researchMode)}
            title="Toggle deep scholarly research analysis"
          >
            <Sparkles className="w-3.5 h-3.5 mr-1" />
            Research Mode
          </button>
        </div>
      </div>

      {/* Selected Monument Context Banner */}
      {selectedSite && (
        <div className="assistant-context-banner">
          <Landmark className="w-3.5 h-3.5 text-amber-400" />
          <span className="context-text">
            Active Context: <strong>{selectedSite.name}</strong> ({selectedSite.state})
          </span>
          {onExploreSite && (
            <button
              className="context-dossier-btn"
              onClick={() => onExploreSite(selectedSite)}
            >
              View Dossier
            </button>
          )}
        </div>
      )}

      {/* Messages Area */}
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

              {/* Citations List */}
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
                        title={`Click to view citation metadata for ${c.source_title}`}
                      >
                        <span className="citation-num">{c.citation_id}</span>
                        <span className="citation-name">{c.source_title}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Evidence Status Pill */}
              {msg.evidenceStatus && (
                <div className="message-footer-meta">
                  <span className={`evidence-badge ${msg.evidenceStatus.toLowerCase()}`}>
                    {msg.evidenceStatus}
                  </span>
                  <span className="timestamp">{msg.timestamp}</span>
                </div>
              )}
            </div>

            {msg.sender === "user" && (
              <div className="user-avatar-badge">
                <User className="w-4 h-4 text-blue-300" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="chat-message bot">
            <div className="bot-avatar-badge">
              <Loader2 className="w-4 h-4 text-amber-300 animate-spin" />
            </div>
            <div className="message-bubble loading-bubble">
              <span className="typing-dots">
                Consulting National Heritage Register & Knowledge Graph...
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompt Chips */}
      <div className="quick-chips-row">
        {RESEARCH_SUGGESTIONS.map((chip) => (
          <button
            key={chip}
            className="chip-btn"
            onClick={() => handleSend(chip)}
            disabled={loading}
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
          placeholder={
            selectedSite
              ? `Ask about ${selectedSite.name}, dynasties, or architecture...`
              : "Ask about documented monuments, dynasties, rulers, or traditions..."
          }
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          disabled={loading}
        />
        <button
          type="submit"
          className="assistant-send-btn"
          aria-label="Send research question"
          disabled={!inputText.trim() || loading}
        >
          {loading ? (
            <Loader2 className="w-4 h-4 text-gray-900 animate-spin" />
          ) : (
            <Send className="w-4 h-4 text-gray-900" />
          )}
        </button>
      </form>

      {/* Citation Details Popover / Modal */}
      {selectedCitation && (
        <div className="citation-modal-backdrop" onClick={() => setSelectedCitation(null)}>
          <div
            className="citation-modal-card"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="citation-modal-header">
              <div className="flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-amber-400" />
                <h4 className="citation-modal-title">
                  Citation {selectedCitation.citation_id}: {selectedCitation.source_title}
                </h4>
              </div>
              <button
                className="citation-close-btn"
                onClick={() => setSelectedCitation(null)}
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="citation-modal-body">
              <div className="citation-meta-item">
                <span className="meta-label">Institution / Publisher:</span>
                <span className="meta-val">
                  {selectedCitation.institution || "Archaeological Survey of India (ASI)"}
                </span>
              </div>

              {selectedCitation.publication_date && (
                <div className="citation-meta-item">
                  <span className="meta-label">Publication / Archive Date:</span>
                  <span className="meta-val">{selectedCitation.publication_date}</span>
                </div>
              )}

              <div className="citation-meta-item">
                <span className="meta-label">Evidence Classification:</span>
                <span className={`evidence-badge ${selectedCitation.evidence_classification.toLowerCase()}`}>
                  {selectedCitation.evidence_classification}
                </span>
              </div>

              {selectedCitation.associated_site_name && (
                <div className="citation-meta-item">
                  <span className="meta-label">Associated Monument:</span>
                  <span className="meta-val">{selectedCitation.associated_site_name}</span>
                </div>
              )}

              <div className="citation-excerpt-box">
                <span className="meta-label block mb-1">Archival Text Excerpt:</span>
                <p className="excerpt-text">{selectedCitation.relevant_excerpt}</p>
              </div>

              {selectedCitation.source_url ? (
                <a
                  href={selectedCitation.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="citation-external-link"
                >
                  Open Archival Document Record <ExternalLink className="w-3.5 h-3.5 ml-1" />
                </a>
              ) : (
                <div className="citation-archival-note">
                  <Info className="w-3.5 h-3.5 inline mr-1 text-gray-400" />
                  Preserved in central national heritage database repository.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AiHeritageAssistant;
