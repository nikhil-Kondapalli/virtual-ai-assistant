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
}

const AudioPlaybackContext = createContext<AudioContextType | null>(null);

export const AudioProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const audioContextRef = useRef<AudioContext | null>(null);
  const queueRef = useRef<{ buffer: AudioBuffer; duration: number }[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const currentTimeRef = useRef(0);

  useEffect(() => {
    if (!audioContextRef.current) {
      audioContextRef.current = new AudioContext();
      currentTimeRef.current = audioContextRef.current.currentTime;
    }

    const playChunk = async (base64Data: string, format?: string) => {
      if (!base64Data || format !== "wav") return;

      try {
        const byteArray = Uint8Array.from(atob(base64Data), (c) =>
          c.charCodeAt(0)
        );
        const audioBuffer = await audioContextRef.current!.decodeAudioData(
          byteArray.buffer.slice(0)
        );

        const startTime = Math.max(
          currentTimeRef.current,
          audioContextRef.current!.currentTime
        );
        const source = audioContextRef.current!.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(audioContextRef.current!.destination);
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
      queueRef.current = [];
      setIsPlaying(false);
    };

    window.addEventListener("tts-chunk", handleChunk as EventListener);
    window.addEventListener("tts-end", handleEnd as EventListener);

    return () => {
      window.removeEventListener("tts-chunk", handleChunk as EventListener);
      window.removeEventListener("tts-end", handleEnd as EventListener);
    };
  }, []);

  const clearQueue = () => {
    queueRef.current = [];
    setIsPlaying(false);
    currentTimeRef.current = audioContextRef.current?.currentTime || 0;
  };

  return (
    <AudioPlaybackContext.Provider value={{ isPlaying, clearQueue }}>
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
