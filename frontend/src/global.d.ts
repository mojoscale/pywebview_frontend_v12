// src/global.d.ts
export {};

declare global {
  //
  // --- PyWebView API typing ---
  //
  interface PyWebViewApi {
    // Known backend methods
    get_version: () => Promise<string>;
    serial_port_available: () => Promise<{ available: boolean; ip?: string }>;
    start_serial_monitor: () => Promise<void>;
    stop_serial_monitor: () => Promise<void>;
    get_platforms: () => Promise<string[]>;
    get_project: (projectId: string) => Promise<any>;
    lint_code: (
      code: string,
      board: string
    ) => Promise<{ errors: { line: number; column?: number; message: string }[] }>;
    compile_project: (args: { projectId: string; code?: string; platform?: string }) => Promise<any>;

    // Catch-all: allows new methods without type errors
    [key: string]: (...args: any[]) => Promise<any>;
  }

  //
  // --- Serial event callbacks ---
  //
  interface Window {
    pywebview?: {
      api: PyWebViewApi;
    };

    /** Called from backend when serial status changes */
    onSerialStatusUpdate?: (connected: boolean) => void;

    /** Called from backend when a new line is received from serial */
    onSerialLine?: (line: string) => void;

    /** Called from backend when compiler/PlatformIO logs are emitted */
    __appendTerminalLog?: (line: string) => void;
  }

  //
  // --- Timeout typing (browser-safe, no NodeJS import needed) ---
  //
  type TimeoutHandle = ReturnType<typeof setTimeout>;
}
