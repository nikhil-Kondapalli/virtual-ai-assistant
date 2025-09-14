import React, { useEffect, useRef, useState } from "react";
import { Live2DManager } from "../live2d/Live2DManager";
import { useLive2DStore } from "../stores/live2dStore";
import { useAudio } from "../audio/AudioProvider";

export const Live2DViewer: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const managerRef = useRef<Live2DManager | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { setInitialized, setError: setStoreError } = useLive2DStore();
  const { isPlaying, audioContext, analyserNode } = useAudio();

  useEffect(() => {
    const initLive2D = async () => {
      if (!containerRef.current || !audioContext || !analyserNode) {
        return;
      }

      try {
        setIsLoading(true);
        setError(null);

        const manager = new Live2DManager();
        await manager.initialize(containerRef.current, analyserNode);

        managerRef.current = manager;
        setInitialized(true);
        setIsLoading(false);

        console.log("Live2D viewer initialized");
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to initialize Live2D";
        setError(errorMessage);
        setStoreError(errorMessage);
        setIsLoading(false);
        console.error("Error initializing Live2D:", err);
      }
    };

    initLive2D();

    return () => {
      if (managerRef.current) {
        managerRef.current.destroy();
        managerRef.current = null;
      }
    };
  }, [setInitialized, setStoreError, audioContext, analyserNode]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (managerRef.current && containerRef.current) {
        const { clientWidth, clientHeight } = containerRef.current;
        managerRef.current.resize(clientWidth, clientHeight);
      }
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Handle talking animation
  useEffect(() => {
    if (managerRef.current) {
      if (isPlaying) {
        managerRef.current.startTalking();
      } else {
        managerRef.current.stopTalking();
      }
    }
  }, [isPlaying]);

  // Handle animation triggers from WebSocket
  useEffect(() => {
    const handleAnimation = (event: CustomEvent) => {
      const { tag } = event.detail;
      if (managerRef.current && tag) {
        managerRef.current.playAnimation(tag);
      }
    };

    window.addEventListener("anim-trigger", handleAnimation as EventListener);
    return () =>
      window.removeEventListener(
        "anim-trigger",
        handleAnimation as EventListener
      );
  }, []);

  // Handle expression triggers
  useEffect(() => {
    const handleExpression = (event: CustomEvent) => {
      const { tag } = event.detail;
      if (managerRef.current && tag) {
        managerRef.current.setExpression(tag);
      }
    };

    window.addEventListener("expr-trigger", handleExpression as EventListener);
    return () => {
      window.removeEventListener(
        "expr-trigger",
        handleExpression as EventListener
      );
    };
  }, []);

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="text-destructive text-6xl mb-4">⚠️</div>
          <h3 className="text-lg font-semibold mb-2">Failed to Load Avatar</h3>
          <p className="text-muted-foreground mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full" style={{ minHeight: "400px" }}>
      <div ref={containerRef} className="live2d-container w-full h-full" />

      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-background/60 backdrop-blur-sm">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading Live2D model...</p>
          </div>
        </div>
      )}

      <div className="absolute top-4 right-4 flex items-center gap-2">
        <div
          className={`w-3 h-3 rounded-full ${
            isPlaying ? "bg-green-500" : "bg-gray-400"
          }`}
        />
        <span className="text-sm text-muted-foreground">
          {isPlaying ? "Speaking" : "Idle"}
        </span>
      </div>
    </div>
  );
};
