import React, { useState } from "react";
import { Bot, Send, User, Landmark } from "lucide-react";
import type { HeritageSite } from "../api";

interface Message {
  id: string;
  sender: "bot" | "user";
  text: string;
  timestamp: string;
}

interface AiHeritageAssistantProps {
  selectedSite: HeritageSite | null;
  onExploreSite?: (site: HeritageSite) => void;
}

const QUICK_CHIPS = ["History", "Architecture", "Nearby Sites", "Preservation"];

export const AiHeritageAssistant: React.FC<AiHeritageAssistantProps> = ({
  selectedSite,
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      sender: "user",
      text: selectedSite
        ? `Tell me about the ${selectedSite.name}?`
        : "Tell me about the Golden Temple?",
      timestamp: "Just now",
    },
    {
      id: "2",
      sender: "bot",
      text: selectedSite
        ? `${selectedSite.name} in ${selectedSite.city || selectedSite.state || "India"} is a protected heritage site (${selectedSite.category || "Monument"}, ${selectedSite.period || "Historical Era"}). ${selectedSite.description || "A national treasure of profound cultural and spiritual significance."}`
        : "The Golden Temple, also known as Harmandir Sahib, is a revered Sikh shrine in Amritsar, Punjab. Celebrated for its sublime gilded sanctum, sacred sarovar, and eternal message of equality and brotherhood.",
      timestamp: "Just now",
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

    // Generate responsive, fact-based response based on selected site or query
    setTimeout(() => {
      let botReply = "";
      const qLower = query.toLowerCase();

      if (selectedSite) {
        if (qLower.includes("history") || qLower.includes("origin")) {
          botReply = `Historical Records for ${selectedSite.name}: Attributed to ${selectedSite.period || "historical era"}. ${selectedSite.significance || selectedSite.description || "Documented by the Archaeological Survey of India."}`;
        } else if (qLower.includes("arch") || qLower.includes("style")) {
          botReply = `Architectural Style: ${selectedSite.architecture || "Traditional Indian monumental architecture"}. Features authentic stone masonry, intricate relief carvings, and historic spatial layout.`;
        } else if (qLower.includes("nearby") || qLower.includes("location")) {
          botReply = `Location: Located in ${selectedSite.city || selectedSite.district || "district"}, ${selectedSite.state || "India"} (Coordinates: ${selectedSite.latitude?.toFixed(4)}, ${selectedSite.longitude?.toFixed(4)}). Connected via national heritage corridors.`;
        } else if (qLower.includes("preserv") || qLower.includes("3d")) {
          botReply = `Preservation Status: Centrally protected monument with high-resolution digital documentation underway under the 3D BHARAT national digital preservation protocol.`;
        } else {
          botReply = `${selectedSite.name} is categorized as ${selectedSite.category || "Monument"} from ${selectedSite.state || "India"}. ${selectedSite.description || ""}`;
        }
      } else {
        botReply = `3D BHARAT currently holds verified national records across Indian states. Select any monument on the map or search above to inspect architectural styles, provenance, and 3D digital scans.`;
      }

      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: "bot",
        text: botReply,
        timestamp: "Just now",
      };

      setMessages((prev) => [...prev, botMsg]);
    }, 400);
  };

  return (
    <div className="assistant-panel-card">
      {/* Panel Header */}
      <div className="panel-header">
        <div className="panel-title-group">
          <Bot className="panel-icon text-cyan-400" />
          <h3 className="panel-title">AI Heritage Assistant</h3>
        </div>
        <div className="online-status-badge">
          <span className="online-indicator-dot" />
          <span>Online</span>
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
            onClick={() => handleSend(`${chip} of ${selectedSite?.name || "the site"}`)}
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
          placeholder="Ask anything..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
        />
        <button
          type="submit"
          className="assistant-send-btn"
          aria-label="Send message"
          disabled={!inputText.trim()}
        >
          <Send className="w-4 h-4 text-gray-900" />
        </button>
      </form>
    </div>
  );
};
export default AiHeritageAssistant;
