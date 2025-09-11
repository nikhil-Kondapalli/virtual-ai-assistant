import { Mic, MicOff, Send, Square } from "lucide-react";
import React, { useEffect, useRef, useState } from "react";
import { useAudio } from "../audio/AudioProvider";
import { useChatStore } from "../stores/chatStore";
import { useWebSocket } from "../ws/WebSocketProvider";

const ChatFooter = () => {
  const { isPlaying, clearQueue } = useAudio();

  return <div>{isPlaying && <span>🔊 Speaking...</span>}</div>;
};

export const ChatInterface: React.FC = () => {
  const [inputMessage, setInputMessage] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { session, currentMessage, setCurrentMessage } = useChatStore();
  const { sendMessage, isConnected, stopGeneration } = useWebSocket();
  const isStreaming = useChatStore(
    (state) =>
      state.session?.messages.some(
        (m) => m.role === "assistant" && m.isStreaming
      ) ?? false
  );

  const isDemoMode = !isConnected && session;

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [session?.messages]);

  const handleSendMessage = () => {
    if (inputMessage.trim() && (isConnected || isDemoMode)) {
      sendMessage(inputMessage);
      setInputMessage("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleVoiceInput = () => {
    console.log("Voice input not implemented yet");
  };

  if (!session) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Connecting to chat...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-container h-full flex flex-col">
      {isDemoMode && (
        <div className="bg-yellow-100 border-b border-yellow-200 p-3">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
            <p className="text-sm text-yellow-800">
              Demo Mode: Backend not connected. You can still chat with Kira!
            </p>
          </div>
        </div>
      )}

      <div className="border-b border-border p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">Chat with Kira</h2>
            <p className="text-sm text-muted-foreground">
              {isConnected
                ? "Connected"
                : isDemoMode
                ? "Demo Mode"
                : "Disconnected"}
            </p>
          </div>
          <div
            className={`w-3 h-3 rounded-full ${
              isConnected
                ? "bg-green-500"
                : isDemoMode
                ? "bg-yellow-500"
                : "bg-red-500"
            }`}
          />
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages flex-1 overflow-y-auto">
        {session.messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="text-4xl mb-4">👋</div>
              <h3 className="text-lg font-semibold mb-2">Hello! I'm Kira</h3>
              <p className="text-muted-foreground">
                Your anime-style virtual assistant. How can I help you today?
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4 p-4">
            {session.messages.map((message) => (
              <div
                key={message.id}
                className={`message-bubble ${
                  message.role === "user" ? "message-user" : "message-assistant"
                }`}
              >
                <div className="flex items-start gap-2">
                  <div className="flex-shrink-0">
                    {message.role === "user" ? (
                      <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                        <span className="text-primary-foreground text-sm font-semibold">
                          U
                        </span>
                      </div>
                    ) : (
                      <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center">
                        <span className="text-secondary-foreground text-sm font-semibold">
                          K
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm">{message.content}</p>
                    {message.isStreaming && (
                      <div className="typing-indicator mt-2">
                        <div className="typing-dot"></div>
                        <div className="typing-dot"></div>
                        <div className="typing-dot"></div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {session.isTyping && (
              <div className="message-bubble message-assistant">
                <div className="flex items-start gap-2">
                  <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center">
                    <span className="text-secondary-foreground text-sm font-semibold">
                      K
                    </span>
                  </div>
                  <div className="typing-indicator">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <ChatFooter />

      <div className="chat-input border-t border-border">
        <div className="flex items-end gap-2 p-4">
          <div className="flex-1">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="w-full p-3 border border-input rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
              rows={1}
              style={{ minHeight: "44px", maxHeight: "120px" }}
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleVoiceInput}
              className={`p-2 rounded-md ${
                isRecording
                  ? "bg-destructive text-destructive-foreground"
                  : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
              }`}
            >
              {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
            </button>
            {isStreaming ? (
              <button onClick={stopGeneration} aria-label="Stop generation">
                <Square className="h-5 w-5" />
              </button>
            ) : (
              <button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || (!isConnected && !isDemoMode)}
                className="p-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send size={20} />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
