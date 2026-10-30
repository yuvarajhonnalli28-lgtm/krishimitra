// Chat widget
import React, { useState, useRef, useEffect } from "react";
import toast from "react-hot-toast";
import "./ChatWidget.css";

const API_BASE_URL = "http://localhost:8000/api";

function ChatWidget() {
  const [messages, setMessages] = useState([
    {
      text: "Hello! I am KrishiMitra AI 🌱. How can I help you with your farm today?",
      sender: "bot",
      timestamp: new Date().toLocaleTimeString()
    }
  ]);

  const [input, setInput] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const recognitionRef = useRef(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Generate session ID
  useEffect(() => {
    const newSessionId = Math.random()
      .toString(36)
      .substring(2, 10);

    setSessionId(newSessionId);
  }, []);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth"
    });
  }, [messages]);

  // Focus input
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Stop speech when component is removed
  useEffect(() => {
    return () => {
      window.speechSynthesis?.cancel();

      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  // ============================================================
  // SPEECH TO TEXT
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
      return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-IN";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      setIsListening(true);
      toast.success("Listening...");
    };

    recognition.onresult = (event) => {
      const transcript =
        event.results[0][0].transcript;

      setInput(transcript);
    };

    recognition.onerror = (event) => {
      console.error(
        "Speech recognition error:",
        event.error
      );

      setIsListening(false);

      if (event.error === "not-allowed") {
        toast.error(
          "Microphone permission was denied. Please allow microphone access."
        );
      } else if (event.error === "no-speech") {
        toast.error("No speech detected. Please try again.");
      } else {
        toast.error(
          "Could not hear you. Please try again."
        );
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    try {
      recognition.start();
    } catch (error) {
      console.error("Microphone start error:", error);
      setIsListening(false);
    }
  };

  // ============================================================
  // TEXT TO SPEECH
  // ============================================================

  const speakText = (text) => {
    if (!("speechSynthesis" in window)) {
      toast.error(
        "Text-to-speech is not supported in this browser."
      );
      return;
    }

    // Stop existing speech
    window.speechSynthesis.cancel();

    const cleanText = text
      .replace(/[*#_~`]/g, "")
      .replace(/---/g, "")
      .replace(/\s+/g, " ")
      .trim();

    const utterance =
      new SpeechSynthesisUtterance(cleanText);

    utterance.lang = "en-IN";
    utterance.rate = 0.9;
    utterance.pitch = 1;

    utterance.onstart = () => {
      setIsSpeaking(true);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
    };

    utterance.onerror = (event) => {
      console.error(
        "Speech synthesis error:",
        event
      );

      setIsSpeaking(false);
    };

    window.speechSynthesis.speak(utterance);
  };

  // Stop voice
  const stopSpeaking = () => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }

    setIsSpeaking(false);
  };

  // ============================================================
  // SEND MESSAGE
  // ============================================================

  const sendMessage = async () => {
    const currentInput = input.trim();

    if (!currentInput) return;

    // Stop microphone
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    }

    const userMessage = {
      text: currentInput,
      sender: "user",
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages((prev) => [
      ...prev,
      userMessage
    ]);

    setInput("");
    setIsTyping(true);

    try {
      // Convert frontend messages to backend format
      const history = messages
        .slice(-5)
        .map((msg) => ({
          role:
            msg.sender === "user"
              ? "user"
              : "assistant",

          content: msg.text,

          timestamp:
            new Date().toISOString()
        }));

      const response = await fetch(
        `${API_BASE_URL}/chat/message`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            message: currentInput,
            session_id: sessionId,
            history: history,
            language: "english"
          })
        }
      );

      if (!response.ok) {
        throw new Error(
          `HTTP error: ${response.status}`
        );
      }

      const data = await response.json();

      const botText =
        data.response ||
        "I'm here to help with your farming questions!";

      const botMessage = {
        text: botText,
        sender: "bot",
        timestamp: new Date().toLocaleTimeString(),
        suggestions: data.suggestions || []
      };

      setMessages((prev) => [
        ...prev,
        botMessage
      ]);

      // Automatically speak AI response
      setTimeout(() => {
        speakText(botText);
      }, 300);

    } catch (error) {
      console.error("Chat error:", error);

      const fallbackMessage = {
        text:
          "I'm having trouble connecting. Please try again in a moment.",
        sender: "bot",
        timestamp: new Date().toLocaleTimeString(),
        isError: true
      };

      setMessages((prev) => [
        ...prev,
        fallbackMessage
      ]);

      toast.error(
        "Failed to get response from AI"
      );

    } finally {
      setIsTyping(false);
    }
  };

  // ============================================================
  // ENTER KEY
  // ============================================================

  const handleKeyPress = (e) => {
    if (
      e.key === "Enter" &&
      !e.shiftKey
    ) {
      e.preventDefault();
      sendMessage();
    }
  };

  // ============================================================
  // SUGGESTIONS
  // ============================================================

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);

    setTimeout(() => {
      sendMessage();
    }, 100);
  };

  // ============================================================
  // CLEAR CHAT
  // ============================================================

  const clearChat = () => {
    stopSpeaking();

    setMessages([
      {
        text:
          "Hello! I am KrishiMitra AI 🌱. How can I help you with your farm today?",
        sender: "bot",
        timestamp:
          new Date().toLocaleTimeString()
      }
    ]);

    setInput("");

    toast.success("Chat cleared");
  };

  // ============================================================
  // SUGGESTED QUESTIONS
  // ============================================================

  const suggestions = [
    "How to grow wheat?",
    "Best fertilizer for tomato",
    "Aphid control",
    "Current potato price",
    "Weather for farming"
  ];

  // ============================================================
  // UI
  // ============================================================

  return (
    <div className="chat-widget-container">

      {/* Chat Toggle */}
      <button
        className={`chat-toggle-btn ${
          isOpen ? "open" : ""
        }`}
        onClick={() =>
          setIsOpen(!isOpen)
        }
      >
        {isOpen ? "✕" : "💬"}

        {!isOpen && (
          <span className="notification-dot"></span>
        )}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="chat-window">

          {/* Header */}
          <div className="chat-header">

            <div className="chat-header-info">
              <h3>🤖 KrishiMitra AI</h3>

              <span className="chat-status">
                Online
              </span>
            </div>

            <div className="chat-header-actions">

              <button
                onClick={clearChat}
                className="clear-btn"
                title="Clear chat"
              >
                🗑️
              </button>

              <button
                onClick={() =>
                  setIsOpen(false)
                }
                className="close-btn"
              >
                ✕
              </button>

            </div>

          </div>

          {/* Messages */}
          <div className="chat-messages">

            {messages.map((msg, index) => (

              <div
                key={index}
                className={`message ${
                  msg.sender === "user"
                    ? "user-message"
                    : "bot-message"
                } ${
                  msg.isError
                    ? "error-message"
                    : ""
                }`}
              >

                <div className="message-avatar">
                  {msg.sender === "user"
                    ? "👤"
                    : "🤖"}
                </div>

                <div className="message-content">

                  <div className="message-text">
                    {msg.text}
                  </div>

                  <div className="message-time">
                    {msg.timestamp}
                  </div>

                  {/* Speaker button for AI */}
                  {msg.sender === "bot" &&
                    !msg.isError && (
                      <button
                        className="speak-btn"
                        onClick={() =>
                          isSpeaking
                            ? stopSpeaking()
                            : speakText(msg.text)
                        }
                        title={
                          isSpeaking
                            ? "Stop speaking"
                            : "Read aloud"
                        }
                      >
                        {isSpeaking
                          ? "⏹️"
                          : "🔊"}
                      </button>
                    )}

                </div>

              </div>

            ))}

            {/* Typing indicator */}
            {isTyping && (
              <div className="message bot-message">

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
          {messages.length < 3 && (
            <div className="suggestions">

              <p className="suggestions-title">
                Try asking:
              </p>

              <div className="suggestion-chips">

                {suggestions.map(
                  (suggestion, index) => (

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
          <div className="chat-input-area">

            <input
              ref={inputRef}
              type="text"
              placeholder="Ask about crops, pests, weather..."
              value={input}
              onChange={(e) =>
                setInput(e.target.value)
              }
              onKeyPress={handleKeyPress}
              className="chat-input"
              disabled={isTyping}
            />

            {/* Microphone */}
            <button
              onClick={startListening}
              className={`mic-btn ${
                isListening
                  ? "listening"
                  : ""
              }`}
              title={
                isListening
                  ? "Stop listening"
                  : "Speak"
              }
              disabled={isTyping}
            >
              {isListening
                ? "⏹️"
                : "🎤"}
            </button>

            {/* Send */}
            <button
              onClick={sendMessage}
              className="send-btn"
              disabled={
                !input.trim() ||
                isTyping
              }
            >
              {isTyping
                ? "..."
                : "📤"}
            </button>

          </div>

          {/* Speaking status */}
          {isSpeaking && (
            <div className="speaking-status">
              🔊 KrishiMitra is speaking...
              <button
                onClick={stopSpeaking}
              >
                Stop
              </button>
            </div>
          )}

          {/* Footer */}
          <div className="chat-footer">
            <span>
              AI-powered farming assistant
            </span>
          </div>

        </div>
      )}

    </div>
  );
}

export default ChatWidget;