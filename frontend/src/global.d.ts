// src/global.d.ts
export {};

declare global {
  //
  // --- PyWebView API typing (backend -> frontend bridge) ---
  //
  interface PyWebViewApi {
    //
    // ---------- General App ----------
    //
    run_update: (download_url: string) => Promise<{ status: string }>;
    get_version: () => Promise<string>;

    //
    // ---------- Projects ----------
    //
    get_projects: () => Promise<any[]>;
    get_project: (project_id: string) => Promise<any>;
    create_project: (details: Record<string, any>) => Promise<void>;
    update_project: (payload: Record<string, any>) => Promise<any>;

    //
    // ---------- Serial + Modules ----------
    //
    serial_port_available: () => Promise<{ available: boolean; ip?: string }>;
    get_module_index: () => Promise<
      | {
          modules: any[];
          success?: boolean;
          error?: string;
        }
      | { success: false; error: string }
    >;

    //
    // ---------- Platforms + Boards ----------
    //
    get_platforms: () => Promise<string[]>;
    get_boards: () => Promise<string[]>;

    //
    // ---------- Linting + Code Intelligence ----------
    //
    lint_code: (
      code: string,
      platform: string
    ) => Promise<{ errors: { line: number; column?: number; message: string }[] }>;
    get_completions: (
      code?: string,
      line?: number,
      column?: number,
      stub_path?: string
    ) => Promise<any[]>;
    format_code_simple: (code: string) => Promise<string>;
    format_code: (code: string) => Promise<string>;

    //
    // ---------- Project Files ----------
    //
    save_project_files: (project_id: string, code: string) => Promise<void>;
    get_project_code: (project_id: string) => Promise<string>;

    //
    // ---------- Compilation ----------
    //
    compile: (
      project_id: string,
      upload?: boolean,
      port?: string | null
    ) => Promise<{ success: boolean; message?: string; error?: string }>;
    get_compile_status: (
      project_id: string
    ) => Promise<{
      completed?: boolean;
      success?: boolean;
      in_progress?: boolean;
      message?: string;
      error?: string;
      warnings?: string[];
      specs?: Record<string, any>;
      suggestions?: string[];
      exists?: boolean;
    }>;
    cancel_compile: (
      project_id: string
    ) => Promise<{ success: boolean; message?: string; error?: string }>;

    //
    // ---------- Environment Variables ----------
    //
    get_all_env: () => Promise<Record<string, any>>;
    get_env_value: (key: string) => Promise<any>;
    create_env_value: (
      key: string,
      value: string,
      is_secret?: boolean
    ) => Promise<any>;
    update_env_value: (
      key: string,
      value?: string,
      is_secret?: boolean
    ) => Promise<any>;
    delete_env_value: (key: string) => Promise<any>;
    bulk_create_env: (pairs: [string, string][]) => Promise<any>;
    bulk_update_env: (pairs: [string, string][]) => Promise<any>;

    //
    // ---------- Serial Monitor ----------
    //
    start_serial_monitor: (baudrate?: number) => Promise<{
      status: "connected" | "error" | "already_running";
      port?: string;
      message?: string;
    }>;
    stop_serial_monitor: () => Promise<{ status: "stopped" | "error"; message?: string }>;
    send_serial_command: (
      command: string
    ) => Promise<{ status: "ok" | "error"; sent?: number; message?: string }>;
    register_serial_callback: () => Promise<{ status: "registered" }>;

    //
    // ---------- Utility ----------
    //
    get_valid_serial_port: (port_hint?: string) => Promise<string | null>;

    //
    // ---------- Catch-all ----------
    //
    [key: string]: (...args: any[]) => Promise<any>;
  }

  //
  // --- Window interface augmentations ---
  //
  interface Window {
    pywebview?: {
      api: PyWebViewApi;
    };

    /** Fired when serial status changes (optional future hook) */
    onSerialStatusUpdate?: (connected: boolean) => void;

    /** Fired when backend pushes a serial line */
    onSerialLine?: (line: string) => void;

    /** Called when compiler/PlatformIO logs stream in */
    __appendTerminalLog?: (line: string) => void;
  }

  //
  // --- Timeout typing (browser-safe, no NodeJS import needed) ---
  //
  type TimeoutHandle = ReturnType<typeof setTimeout>;
}
