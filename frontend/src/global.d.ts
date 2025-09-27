export {};

declare global {
  interface Window {
    pywebview?: {
      api?: Record<string, (...args: any[]) => Promise<any>>; // ✅ generic fallback
    };
    onSerialStatusUpdate?: (connected: boolean) => void;
    onSerialLine?: (line: string) => void;
  }
}
