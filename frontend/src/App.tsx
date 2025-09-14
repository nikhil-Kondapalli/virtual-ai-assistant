import React from "react";
import { ChatInterface } from "./components/ChatInterface";
import { Live2DViewer } from "./components/Live2DViewer";
import { WebSocketProvider } from "./ws/WebSocketProvider";
import { AudioProvider } from "./audio/AudioProvider";

function App() {
  return (
    <WebSocketProvider>
      <AudioProvider>
        <div className="flex h-screen bg-background">
          <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-950 dark:to-purple-950">
            <Live2DViewer />
          </div>

          <div className="w-96 border-l border-border bg-card">
            <ChatInterface />
          </div>
        </div>
      </AudioProvider>
    </WebSocketProvider>
  );
}

export default App;
