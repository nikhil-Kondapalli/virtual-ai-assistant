import { Mic, MicOff, Send, Square } from "lucide-react";
import React, { useEffect, useRef, useState } from "react";
import { useAudio } from "@audio/audio-provider";
import { useChatStore } from "@stores/chat-store";
import { useWebSocket } from "@ws/web-socket-provider";

const ChatFooter = () => {
  const { isPlaying } = useAudio();

  return (
    <div className="h-8 px-4 flex items-center text-sm text-muted-foreground">
      {isPlaying && (
        <span className="flex items-center gap-2">🔊 Speaking...</span>
      )}
    </div>
  );
};

export const ChatInterface: React.FC = () => {
  const [inputMessage, setInputMessage] = useState("");
  const [isRecording] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { session } = useChatStore();
  const { sendMessage, isConnected, stopGeneration } = useWebSocket();
  const isStreaming = useChatStore(
    state =>
      state.session?.messages.some(
        m => m.role === "assistant" && m.isStreaming
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
    <div className="bg-background h-full flex flex-col">
      {isDemoMode && (
        <div className="bg-secondary/20 border-b border-secondary/30 p-3">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-secondary rounded-full"></div>
            <p className="text-sm text-secondary-foreground">
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
              {(() => {
                if (isConnected) return "Connected";
                if (isDemoMode) return "Demo Mode";
                return "Disconnected";
              })()}
            </p>
          </div>
          <div
            className={`w-3 h-3 rounded-full ${(() => {
              if (isConnected) return "bg-green-500";
              if (isDemoMode) return "bg-secondary";
              return "bg-destructive";
            })()}`}
          />
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        {session.messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="text-4xl mb-4">👋</div>
              <h3 className="text-lg font-semibold mb-2">
                Hello! I&apos;m Kira
              </h3>
              <p className="text-muted-foreground">
                Your Virtual AI assistant. How can I help you today?
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4 p-4">
            {session.messages.map(message => (
              <div
                key={message.id}
                className={`flex gap-2 items-end ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {message.role === "assistant" && (
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center">
                      <span className="text-secondary-foreground text-sm font-semibold">
                        K
                      </span>
                    </div>
                  </div>
                )}
                <div
                  className={`rounded-lg p-3 max-w-[80%] ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-foreground"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">
                    {message.content}
                  </p>
                  {message.isStreaming && (
                    <div className="flex items-center space-x-1 mt-2">
                      <div className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                      <div className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                      <div className="w-2 h-2 bg-current rounded-full animate-bounce"></div>
                    </div>
                  )}
                </div>
                {message.role === "user" && (
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                      <span className="text-primary-foreground text-sm font-semibold">
                        U
                      </span>
                    </div>
                  </div>
                )}
              </div>
            ))}

            {/* Typing indicator */}
            {session.isTyping && (
              <div className="flex gap-2 items-end justify-start">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center">
                    <span className="text-secondary-foreground text-sm font-semibold">
                      K
                    </span>
                  </div>
                </div>
                <div className="rounded-lg p-3 bg-muted">
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <ChatFooter />

      <div className="border-t border-border bg-background">
        <div className="flex items-end gap-2 p-4">
          <div className="flex-1">
            <textarea
              value={inputMessage}
              onChange={e => {
                setInputMessage(e.target.value);
              }}
              onKeyDown={handleKeyPress}
              placeholder="Type your message..."
              className="w-full p-3 bg-background border border-input rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
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
              <button
                onClick={stopGeneration}
                aria-label="Stop generation"
                className="p-2 bg-destructive text-destructive-foreground rounded-md hover:bg-destructive/90"
              >
                <Square size={20} />
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
