// AI advisor page
import React, {
  useState,
  useEffect,
  useContext,
  useRef
} from "react";

import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import toast from "react-hot-toast";

import "./AIAdvisor.css";

const API_BASE_URL = "http://localhost:8000/api";

// ============================================================
// SUPPORTED LANGUAGES
// ============================================================

const LANGUAGES = {
  english: {
    name: "English",
    speechCode: "en-IN"
  },

  kannada: {
    name: "ಕನ್ನಡ (Kannada)",
    speechCode: "kn-IN"
  },

  hindi: {
    name: "हिन्दी (Hindi)",
    speechCode: "hi-IN"
  },

  telugu: {
    name: "తెలుగు (Telugu)",
    speechCode: "te-IN"
  },

  tamil: {
    name: "தமிழ் (Tamil)",
    speechCode: "ta-IN"
  },

  marathi: {
    name: "मराठी (Marathi)",
    speechCode: "mr-IN"
  }
};


// ============================================================
// AI ADVISOR
// ============================================================

function AIAdvisor() {
  const { user } = useContext(AuthContext);

  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  // ----------------------------------------------------------
  // Chat messages
  // ----------------------------------------------------------

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "👋 **Namaste!** I'm your KrishiMitra AI farming assistant. How can I help you with your farm today?",
      timestamp: new Date().toISOString()
    }
  ]);

  // ----------------------------------------------------------
  // State
  // ----------------------------------------------------------

  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  // Language
  const [selectedLanguage, setSelectedLanguage] =
    useState("english");

  // Speech
  const [isListening, setIsListening] =
    useState(false);

  const [isSpeaking, setIsSpeaking] =
    useState(false);

  const [suggestions, setSuggestions] = useState([
    "How to grow wheat?",
    "Best fertilizer for tomato",
    "Aphid control in mustard",
    "Current potato price",
    "Weather impact on crops"
  ]);

  const [chatInfo, setChatInfo] = useState(null);


  // ============================================================
  // SCROLL
  // ============================================================

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({
        behavior: "smooth"
      });
    }
  };


  // ============================================================
  // INITIALIZE
  // ============================================================

  useEffect(() => {
    fetchChatInfo();

    const existingSession =
      localStorage.getItem("chatSessionId");

    if (existingSession) {
      setSessionId(existingSession);
    } else {
      const newSession =
        Math.random()
          .toString(36)
          .substring(2, 10);

      localStorage.setItem(
        "chatSessionId",
        newSession
      );

      setSessionId(newSession);
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }

      if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);


  // ============================================================
  // CHAT INFO
  // ============================================================

  const fetchChatInfo = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/chat/`
      );

      if (response.ok) {
        const data = await response.json();
        setChatInfo(data);
      }
    } catch (error) {
      console.error(
        "Failed to fetch chat info:",
        error
      );
    }
  };


  // ============================================================
  // CHANGE LANGUAGE
  // ============================================================

  const handleLanguageChange = (language) => {
    // Stop current speech
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }

    setIsSpeaking(false);

    // Stop microphone
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }

    setIsListening(false);

    setSelectedLanguage(language);

    toast.success(
      `Language changed to ${LANGUAGES[language].name}`,
      {
        duration: 1500
      }
    );
  };


  // ============================================================
  // GET SPEECH LANGUAGE
  // ============================================================

  const getSpeechLanguage = () => {
    return (
      LANGUAGES[selectedLanguage]?.speechCode ||
      "en-IN"
    );
  };


  // ============================================================
  // 🎤 SPEECH TO TEXT
  // ============================================================

  const startListening = () => {
    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      toast.error(
        "Speech recognition is not supported. Please use Chrome or Edge."
      );

      return;
    }

    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      return;
    }

    const recognition =
      new SpeechRecognition();

    recognition.lang =
      getSpeechLanguage();

    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      setIsListening(true);

      toast.success(
        `🎤 Listening in ${LANGUAGES[selectedLanguage].name}`,
        {
          duration: 1500
        }
      );
    };

    recognition.onresult = (event) => {
      const transcript =
        event.results[0][0].transcript;

      setInputMessage(transcript);
    };

    recognition.onerror = (event) => {
      console.error(
        "Speech recognition error:",
        event.error
      );

      setIsListening(false);

      if (event.error === "not-allowed") {
        toast.error(
          "Microphone permission denied. Please allow microphone access."
        );
      } else if (
        event.error === "no-speech"
      ) {
        toast.error(
          "No speech detected. Please try again."
        );
      } else {
        toast.error(
          "Could not hear you. Please try again."
        );
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current =
      recognition;

    try {
      recognition.start();
    } catch (error) {
      console.error(
        "Could not start microphone:",
        error
      );

      setIsListening(false);
    }
  };


  // ============================================================
  // 🔊 TEXT TO SPEECH
  // ============================================================

  const speakText = (text) => {
    if (!("speechSynthesis" in window)) {
      toast.error(
        "Text-to-speech is not supported in this browser."
      );

      return;
    }

    window.speechSynthesis.cancel();

    const cleanText = text
      .replace(/\*\*/g, "")
      .replace(/###/g, "")
      .replace(/##/g, "")
      .replace(/#/g, "")
      .replace(/\*/g, "")
      .replace(/---/g, "")
      .replace(/`/g, "")
      .replace(/\s+/g, " ")
      .trim();

    if (!cleanText) return;

    const utterance =
      new SpeechSynthesisUtterance(
        cleanText
      );

    utterance.lang =
      getSpeechLanguage();

    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;

    // Try to find a matching voice
    const voices =
      window.speechSynthesis.getVoices();

    const matchingVoice =
      voices.find(
        (voice) =>
          voice.lang
            .toLowerCase()
            .startsWith(
              getSpeechLanguage()
                .split("-")[0]
                .toLowerCase()
            )
      );

    if (matchingVoice) {
      utterance.voice =
        matchingVoice;
    }

    utterance.onstart = () => {
      setIsSpeaking(true);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
    };

    utterance.onerror = (event) => {
      console.error(
        "Text-to-speech error:",
        event
      );

      setIsSpeaking(false);
    };

    window.speechSynthesis.speak(
      utterance
    );
  };


  // ============================================================
  // STOP SPEAKING
  // ============================================================

  const stopSpeaking = () => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }

    setIsSpeaking(false);
  };


  // ============================================================
  // SEND MESSAGE
  // ============================================================

  const sendMessage = async (
    messageText = inputMessage
  ) => {
    if (loading) return;

    if (!messageText.trim()) return;

    if (!user) {
      toast.error(
        "Please login to chat with AI Advisor",
        {
          icon: "🔒",
          duration: 3000
        }
      );

      return;
    }

    // Stop microphone
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    }

    // Stop previous speech
    stopSpeaking();

    const userMessage = {
      role: "user",
      content: messageText,
      timestamp:
        new Date().toISOString()
    };

    setMessages((prev) => [
      ...prev,
      userMessage
    ]);

    setInputMessage("");
    setLoading(true);

    try {
      // Correct Gemini history format
      const chatHistory =
        messages
          .filter(
            (msg) =>
              msg.role !== "system"
          )
          .slice(-6)
          .map((msg) => ({
            role: msg.role,
            content: msg.content,
            timestamp: msg.timestamp
          }));

      const response =
        await fetch(
          `${API_BASE_URL}/chat/message`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json"
            },

            body: JSON.stringify({
              message: messageText,
              session_id: sessionId,
              history: chatHistory,

              // Selected language
              language:
                selectedLanguage,

              farmer_id:
                user?.id || null
            })
          }
        );

      if (!response.ok) {
        let errorMessage =
          "Failed to get response";

        try {
          const error =
            await response.json();

          errorMessage =
            error.detail ||
            errorMessage;
        } catch {
          // Ignore parsing error
        }

        throw new Error(
          errorMessage
        );
      }

      const data =
        await response.json();

      const assistantText =
        data.response ||
        "I'm here to help with your farming questions!";

      const assistantMessage = {
        role: "assistant",
        content: assistantText,

        timestamp:
          data.timestamp ||
          new Date().toISOString(),

        confidence:
          data.confidence,

        category:
          data.category,

        follow_up:
          data.follow_up_questions ||
          [],

        action_items:
          data.action_items ||
          []
      };

      setMessages((prev) => [
        ...prev,
        assistantMessage
      ]);

      // Update suggestions
      if (
        data.suggestions &&
        data.suggestions.length > 0
      ) {
        setSuggestions(
          data.suggestions
        );
      }

      // Automatically speak response
      setTimeout(() => {
        speakText(assistantText);
      }, 400);

    } catch (error) {
      console.error(
        "Chat error:",
        error
      );

      toast.error(
        error.message ||
          "Failed to send message"
      );

    } finally {
      setLoading(false);
    }
  };


  // ============================================================
  // FORM
  // ============================================================

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage();
  };


  // ============================================================
  // SUGGESTION
  // ============================================================

  const handleSuggestionClick = (
    suggestion
  ) => {
    sendMessage(suggestion);
  };


  // ============================================================
  // ENTER
  // ============================================================

  const handleKeyDown = (e) => {
    if (
      e.key === "Enter" &&
      !e.shiftKey
    ) {
      e.preventDefault();
      sendMessage();
    }
  };


  // ============================================================
  // CLEAR CHAT
  // ============================================================

  const handleClearChat = () => {
    if (
      window.confirm(
        "Clear chat history?"
      )
    ) {
      stopSpeaking();

      setMessages([
        {
          role: "assistant",
          content:
            "👋 **Namaste!** I'm your KrishiMitra AI farming assistant. How can I help you with your farm today?",
          timestamp:
            new Date().toISOString()
        }
      ]);

      setInputMessage("");

      toast.success(
        "Chat cleared"
      );
    }
  };


  // ============================================================
  // FORMAT TIME
  // ============================================================

  const formatTime = (
    timestamp
  ) => {
    return new Date(
      timestamp
    ).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit"
    });
  };


  // ============================================================
  // RENDER MESSAGE
  // ============================================================

  const renderMessage = (
    content
  ) => {
    const parts =
      content.split(
        /(\*\*.*?\*\*)/g
      );

    return parts.map(
      (part, index) => {
        if (
          part.startsWith("**") &&
          part.endsWith("**")
        ) {
          return (
            <strong key={index}>
              {part.slice(2, -2)}
            </strong>
          );
        }

        return part;
      }
    );
  };


  // ============================================================
  // LOGIN
  // ============================================================

  if (!user) {
    return (
      <div className="advisor-login-prompt">

        <div className="lock-icon">
          🔒
        </div>

        <h2>
          Login Required
        </h2>

        <p>
          Please login to access
          the AI Advisor and get
          personalized farming
          advice.
        </p>

        <Link
          to="/login"
          className="btn btn-primary"
        >
          Login to Continue
        </Link>

        <p className="guest-note">
          New here?{" "}
          <Link to="/signup">
            Create an account
          </Link>{" "}
          - It's free!
        </p>

      </div>
    );
  }


  // ============================================================
  // MAIN PAGE
  // ============================================================

  return (
    <div className="advisor-page">

      {/* Header */}
      <div className="advisor-header">

        <div className="advisor-title">

          <h1>
            🤖 AI Farming Advisor
          </h1>

          <p>
            Ask me anything about
            farming, crops, pests,
            or markets
          </p>

        </div>

        <div className="advisor-actions">

          <button
            onClick={
              handleClearChat
            }
            className="btn btn-outline"
          >
            🗑️ Clear
          </button>

        </div>

      </div>


      {/* Language Selector */}
      <div className="language-selector">

        <label htmlFor="language">
          🌐 Language:
        </label>

        <select
          id="language"
          value={selectedLanguage}
          onChange={(e) =>
            handleLanguageChange(
              e.target.value
            )
          }
        >

          {Object.entries(
            LANGUAGES
          ).map(
            ([
              key,
              language
            ]) => (
              <option
                key={key}
                value={key}
              >
                {language.name}
              </option>
            )
          )}

        </select>

      </div>


      {/* Chat Info */}
      {chatInfo && (
        <div className="chat-info-banner">

          <span>
            ✨{" "}
            {chatInfo.capabilities
              ?.length || 5}
            + farming topics
          </span>

          <span>
            🌱{" "}
            {LANGUAGES[
              selectedLanguage
            ].name}
          </span>

        </div>
      )}


      {/* Chat Container */}
      <div className="chat-container">

        {/* Messages */}
        <div className="messages-area">

          {messages.map(
            (msg, index) => (

              <div
                key={index}
                className={`message ${
                  msg.role === "user"
                    ? "user-message"
                    : "assistant-message"
                }`}
              >

                <div className="message-avatar">
                  {msg.role === "user"
                    ? "👤"
                    : "🤖"}
                </div>

                <div className="message-content">

                  <div className="message-header">

                    <span className="message-sender">
                      {msg.role ===
                      "user"
                        ? "You"
                        : "KrishiMitra AI"}
                    </span>

                    <span className="message-time">
                      {formatTime(
                        msg.timestamp
                      )}
                    </span>

                  </div>

                  <div className="message-text">
                    {renderMessage(
                      msg.content
                    )}
                  </div>


                  {/* Speaker */}
                  {msg.role ===
                    "assistant" && (

                    <div className="voice-controls">

                      <button
                        type="button"
                        className="speak-button"
                        onClick={() =>
                          isSpeaking
                            ? stopSpeaking()
                            : speakText(
                                msg.content
                              )
                        }
                      >
                        {isSpeaking
                          ? "⏹️ Stop"
                          : "🔊 Listen"}
                      </button>

                    </div>
                  )}


                  {/* Confidence */}
                  {msg.role ===
                    "assistant" &&
                    msg.confidence && (

                    <div className="message-confidence">
                      Confidence:{" "}
                      {Math.round(
                        msg.confidence *
                          100
                      )}
                      %
                    </div>
                  )}


                  {/* Action Items */}
                  {msg.role ===
                    "assistant" &&
                    msg.action_items
                      ?.length > 0 && (

                    <div className="action-items">

                      <strong>
                        📋 Action Items:
                      </strong>

                      <ul>

                        {msg.action_items.map(
                          (
                            item,
                            i
                          ) => (
                            <li key={i}>
                              {item}
                            </li>
                          )
                        )}

                      </ul>

                    </div>
                  )}


                  {/* Follow-up */}
                  {msg.role ===
                    "assistant" &&
                    msg.follow_up
                      ?.length > 0 && (

                    <div className="follow-up">

                      <strong>
                        💡 You might also ask:
                      </strong>

                      <div className="follow-up-buttons">

                        {msg.follow_up.map(
                          (
                            question,
                            i
                          ) => (

                            <button
                              key={i}
                              className="follow-up-btn"
                              onClick={() =>
                                handleSuggestionClick(
                                  question
                                )
                              }
                            >
                              {question}
                            </button>

                          )
                        )}

                      </div>

                    </div>
                  )}

                </div>

              </div>
            )
          )}


          {/* Loading */}
          {loading && (

            <div className="message assistant-message">

              <div className="message-avatar">
                🤖
              </div>

              <div className="message-content">

                <div className="typing-indicator">

                  <span></span>
                  <span></span>
                  <span></span>

                </div>

              </div>

            </div>
          )}

          <div ref={messagesEndRef} />

        </div>


        {/* Suggestions */}
        {suggestions.length > 0 &&
          !loading && (

            <div className="suggestions-area">

              <p className="suggestions-title">
                💬 Suggested questions:
              </p>

              <div className="suggestions-list">

                {suggestions.map(
                  (
                    suggestion,
                    index
                  ) => (

                    <button
                      key={index}
                      className="suggestion-chip"
                      onClick={() =>
                        handleSuggestionClick(
                          suggestion
                        )
                      }
                    >
                      {suggestion}
                    </button>

                  )
                )}

              </div>

            </div>
          )}


        {/* Input */}
        <form
          onSubmit={handleSubmit}
          className="chat-input-form"
        >

          <input
            type="text"
            value={inputMessage}
            onChange={(e) =>
              setInputMessage(
                e.target.value
              )
            }
            onKeyDown={
              handleKeyDown
            }
            placeholder={`Ask in ${
              LANGUAGES[
                selectedLanguage
              ].name
            }...`}
            className="chat-input"
            disabled={loading}
          />


          {/* Microphone */}
          <button
            type="button"
            onClick={
              startListening
            }
            className={`mic-button ${
              isListening
                ? "listening"
                : ""
            }`}
            disabled={loading}
            title={
              isListening
                ? "Stop listening"
                : "Speak"
            }
          >
            {isListening
              ? "⏹️"
              : "🎤"}
          </button>


          {/* Send */}
          <button
            type="submit"
            className="send-button"
            disabled={
              loading ||
              !inputMessage.trim()
            }
          >
            {loading
              ? "..."
              : "📤 Send"}
          </button>

        </form>


        {/* Speaking Status */}
        {isSpeaking && (

          <div className="speaking-status">

            <span>
              🔊 KrishiMitra is
              speaking in{" "}
              {
                LANGUAGES[
                  selectedLanguage
                ].name
              }
              ...
            </span>

            <button
              type="button"
              onClick={
                stopSpeaking
              }
            >
              ⏹️ Stop
            </button>

          </div>
        )}


        {/* Quick Actions */}
        <div className="quick-actions">

          <button
            className="quick-action-btn"
            onClick={() =>
              handleSuggestionClick(
                "What crops should I plant this season?"
              )
            }
          >
            🌱 Crop Planning
          </button>

          <button
            className="quick-action-btn"
            onClick={() =>
              handleSuggestionClick(
                "How to control pests naturally?"
              )
            }
          >
            🐛 Pest Control
          </button>

          <button
            className="quick-action-btn"
            onClick={() =>
              handleSuggestionClick(
                "Best fertilizer for vegetables"
              )
            }
          >
            🧪 Fertilizer
          </button>

          <button
            className="quick-action-btn"
            onClick={() =>
              handleSuggestionClick(
                "Current market prices"
              )
            }
          >
            💰 Market Prices
          </button>

        </div>

      </div>


      {/* Footer */}
      <div className="advisor-footer">

        <p>
          ⚠️ AI-generated advice.
          Always consult with local
          agricultural experts for
          critical decisions.

          <br />

          <Link to="/feedback">
            Give Feedback
          </Link>{" "}
          to help us improve.
        </p>

      </div>

    </div>
  );
}

export default AIAdvisor;