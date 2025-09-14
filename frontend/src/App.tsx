import { ChatInterface } from "@components/chat-interface";
import { Live2DViewer } from "@components/live-2d-viewer";
import type { ReactElement } from "react";
import { AudioProvider } from "./audio/audio-provider";
import { WebSocketProvider } from "./ws/web-socket-provider";

const App = (): ReactElement => {
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
};

export { App };
