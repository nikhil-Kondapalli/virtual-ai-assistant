import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";

interface AudioContextType {
  isPlaying: boolean;
  clearQueue: () => void;
  audioContext: AudioContext | null;
  analyserNode: AnalyserNode | null;
}

const AudioPlaybackContext = createContext<AudioContextType | null>(null);

export const AudioProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [audioContext, setAudioContext] = useState<AudioContext | null>(null);
  const [analyserNode, setAnalyserNode] = useState<AnalyserNode | null>(null);
  const queueRef = useRef<{ buffer: AudioBuffer; duration: number }[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const currentTimeRef = useRef(0);

  useEffect(() => {
    const context = new AudioContext();
    const analyser = context.createAnalyser();
    analyser.connect(context.destination);
    setAudioContext(context);
    setAnalyserNode(analyser);
    currentTimeRef.current = context.currentTime;
  }, []);

  useEffect(() => {
    if (!audioContext || !analyserNode) return;

    const playChunk = async (base64Data: string, format?: string) => {
      if (!base64Data || format !== "opus") return;

      try {
        const byteArray = Uint8Array.from(atob(base64Data), (c) =>
          c.charCodeAt(0)
        );
        const audioBuffer = await audioContext.decodeAudioData(
          byteArray.buffer.slice(0)
        );

        const startTime = Math.max(
          currentTimeRef.current,
          audioContext.currentTime
        );
        const source = audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(analyserNode);
        source.start(startTime);

        currentTimeRef.current = startTime + audioBuffer.duration;
        queueRef.current.push({
          buffer: audioBuffer,
          duration: audioBuffer.duration,
        });

        setIsPlaying(true);

        source.onended = () => {
          queueRef.current.shift();
          if (queueRef.current.length === 0) {
            setIsPlaying(false);
          }
        };
      } catch (err) {
        console.error("❌ Failed to play audio chunk:", err);
      }
    };

    const handleChunk = (event: Event) => {
      const { data, format } = (event as CustomEvent).detail;
      playChunk(data, format);
    };

    const handleEnd = () => {
      console.log("✅ TTS stream ended");
    };

    window.addEventListener("tts-chunk", handleChunk as EventListener);
    window.addEventListener("tts-end", handleEnd as EventListener);

    return () => {
      window.removeEventListener("tts-chunk", handleChunk as EventListener);
      window.removeEventListener("tts-end", handleEnd as EventListener);
    };
  }, [audioContext, analyserNode]);

  const clearQueue = () => {
    queueRef.current = [];
    setIsPlaying(false);
    currentTimeRef.current = audioContext?.currentTime || 0;
  };

  return (
    <AudioPlaybackContext.Provider
      value={{
        isPlaying,
        clearQueue,
        audioContext,
        analyserNode,
      }}
    >
      {children}
    </AudioPlaybackContext.Provider>
  );
};

export const useAudio = () => {
  const ctx = useContext(AudioPlaybackContext);
  if (!ctx) {
    throw new Error("useAudio must be used within an AudioProvider");
  }
  return ctx;
};
