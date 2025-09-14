import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import { useChatStore } from "../stores/chat-store";
import { useLive2DStore } from "../stores/live-2d-store";

interface WebSocketContextType {
  sendMessage: (message: string) => void;
  stopGeneration: () => void;
  isConnected: boolean;
  sessionId: string | null;
}

const WebSocketContext = createContext<WebSocketContextType | null>(null);

interface WebSocketProviderProps {
  children: React.ReactNode;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({
  children,
}) => {
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isDemoMode, setIsDemoMode] = useState(false);

  const { setSession, addMessage, updateMessage, setConnected, setTyping } =
    useChatStore();
  const { setAnimation } = useLive2DStore();

  const handleWebSocketMessage = useCallback(
    (data: any) => {
      const { type, id, token, tag, seq, format, data: payload } = data;

      switch (type) {
        case "meta":
          setSessionId(id);
          setSession({
            id,
            persona: data.persona || "kira_v1",
            messages: [],
            isConnected: true,
            isTyping: false,
          });
          break;

        case "llm_token":
          if (token) {
            const existingMessage = useChatStore
              .getState()
              .session?.messages.find(
                (m) => m.role === "assistant" && m.isStreaming
              );

            if (existingMessage) {
              updateMessage(existingMessage.id, {
                content: existingMessage.content + token,
              });
            } else {
              addMessage({
                role: "assistant",
                content: token,
                isStreaming: true,
              });
            }
          }
          break;

        case "llm_end":
          const streamingMessage = useChatStore
            .getState()
            .session?.messages.find(
              (m) => m.role === "assistant" && m.isStreaming
            );
          if (streamingMessage) {
            updateMessage(streamingMessage.id, { isStreaming: false });
          }
          break;

        case "tts_chunk":
          window.dispatchEvent(
            new CustomEvent("tts-chunk", {
              detail: { seq, format, data: payload },
            })
          );
          break;

        case "tts_end":
          window.dispatchEvent(
            new CustomEvent("tts-end", {
              detail: { totalChunks: data.total_chunks },
            })
          );
          break;

        case "anim":
          if (tag) setAnimation(tag);
          break;

        case "system":
          console.log("ℹ️ System message:", data.message || payload);
          addMessage({
            role: "system",
            content: data.message || JSON.stringify(payload),
          });
          break;

        case "end":
          console.log("🔚 Session ended");
          break;

        case "error":
          console.error("❌ Backend error:", data.error);
          break;

        default:
          console.warn("⚠️ Unknown WebSocket message type:", type, data);
      }
    },
    [setSessionId, setSession, updateMessage, addMessage, setAnimation]
  );

  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const ws = new WebSocket("ws://localhost:8000/ws/chat/demo/");
        wsRef.current = ws;

        ws.onopen = () => {
          console.log("✅ WebSocket connected");
          setIsConnected(true);
          setConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
          } catch (error) {
            console.error("❌ Error parsing WebSocket message:", error);
          }
        };

        ws.onclose = () => {
          console.log("⚠️ WebSocket disconnected");
          setIsConnected(false);
          setConnected(false);
          setTimeout(connectWebSocket, 3000); // auto-reconnect
        };

        ws.onerror = (error) => {
          console.error("❌ WebSocket error:", error);
          if (!isDemoMode) {
            setIsDemoMode(true);
            setConnected(true);
            console.log("🚨 Switching to demo mode");
          }
        };
      } catch (error) {
        console.error("❌ Error creating WebSocket connection:", error);
        if (!isDemoMode) {
          setIsDemoMode(true);
          setConnected(true);
          console.log("🚨 Switching to demo mode");
        }
        setTimeout(connectWebSocket, 3000);
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }
    };
  }, [setConnected, isDemoMode, handleWebSocketMessage]);

  const sendMessage = (message: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const data = { type: "user_message", message: message.trim() };
      wsRef.current.send(JSON.stringify(data));

      addMessage({ role: "user", content: message.trim() });
      setTyping(true);
      setTimeout(() => setTyping(false), 2000);
    } else if (isDemoMode) {
      addMessage({ role: "user", content: message.trim() });
      setTyping(true);
      setTimeout(() => {
        setTyping(false);
        addMessage({
          role: "assistant",
          content: `Hello! I'm Kira 🎌✨. You said: "${message.trim()}". (Demo mode active)`,
        });
        setAnimation("happy");
        setTimeout(() => setAnimation("talking"), 1000);
        setTimeout(() => setAnimation("smile"), 3000);
      }, 1500);
    }
  };

  const stopGeneration = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      console.log("🛑 Sending stop generation request");
      const data = { type: "stop_generation" };
      wsRef.current.send(JSON.stringify(data));
    } else {
      console.warn("Cannot stop generation: WebSocket is not connected.");
    }
  };

  const contextValue: WebSocketContextType = {
    sendMessage,
    stopGeneration,
    isConnected,
    sessionId,
  };

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error("useWebSocket must be used within a WebSocketProvider");
  }
  return context;
};
