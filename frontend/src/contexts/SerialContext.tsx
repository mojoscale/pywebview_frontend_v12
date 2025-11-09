import React, { createContext, useContext, useState, useEffect } from "react";

interface SerialContextType {
  terminalLogs: string[];
  serialConnected: boolean;
  monitoring: boolean;
  clearTerminal: () => void;
  startMonitoring: () => Promise<void>;
  stopMonitoring: () => Promise<void>;
  sendCommand: (cmd: string) => Promise<void>;
}

const SerialContext = createContext<SerialContextType | null>(null);

export const SerialProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [terminalLogs, setTerminalLogs] = useState<string[]>([]);
  const [serialConnected, setSerialConnected] = useState(false);
  const [monitoring, setMonitoring] = useState(false);

  // 🔹 Listen for logs from backend
  useEffect(() => {
    const handleSerialLog = (event: CustomEvent) => {
      setTerminalLogs((prev) => [...prev, event.detail]);
    };

    window.addEventListener("serial-log", handleSerialLog as EventListener);
    return () => window.removeEventListener("serial-log", handleSerialLog as EventListener);
  }, []);

  // 🔹 Clear all logs
  const clearTerminal = () => setTerminalLogs([]);

  // 🔹 Start serial monitoring (backend auto-detects port)
  const startMonitoring = async () => {
    try {
      if (!window.pywebview?.api?.start_serial_monitor) {
        console.warn("PyWebView API not available yet");
        return;
      }
      const res = await window.pywebview.api.start_serial_monitor();
      if (res.status === "connected") {
        setSerialConnected(true);
        setMonitoring(true);
        setTerminalLogs((prev) => [...prev, `🚀 Connected to ${res.port}`]);
      } else {
        setTerminalLogs((prev) => [...prev, `❌ ${res.message || "Failed to connect"}`]);
      }
    } catch (err: any) {
      setTerminalLogs((prev) => [...prev, `❌ ${err.message || err}`]);
    }
  };

  // 🔹 Stop monitoring
  const stopMonitoring = async () => {
    try {
      if (!window.pywebview?.api?.stop_serial_monitor) {
        console.warn("PyWebView API not available yet");
        return;
      }
      const res = await window.pywebview.api.stop_serial_monitor();
      if (res.status === "stopped") {
        setSerialConnected(false);
        setMonitoring(false);
        setTerminalLogs((prev) => [...prev, "🛑 Monitoring stopped"]);
      }
    } catch (err: any) {
      setTerminalLogs((prev) => [...prev, `❌ ${err.message || err}`]);
    }
  };

  // 🔹 Send a command to backend
  const sendCommand = async (cmd: string) => {
    if (!cmd.trim()) return;
    setTerminalLogs((prev) => [...prev, `> ${cmd}`]);
    try {
      if (!window.pywebview?.api?.send_serial_command) {
        console.warn("PyWebView API not available yet");
        return;
      }
      const res = await window.pywebview.api.send_serial_command(cmd);
      if (res.status === "ok") {
        setTerminalLogs((prev) => [...prev, `📤 Sent ${res.sent} bytes`]);
      } else {
        setTerminalLogs((prev) => [...prev, `❌ ${res.message || "Error sending command"}`]);
      }
    } catch (err: any) {
      setTerminalLogs((prev) => [...prev, `❌ ${err.message || err}`]);
    }
  };

  return (
    <SerialContext.Provider
      value={{
        terminalLogs,
        serialConnected,
        monitoring,
        clearTerminal,
        startMonitoring,
        stopMonitoring,
        sendCommand,
      }}
    >
      {children}
    </SerialContext.Provider>
  );
};

export const useSerial = () => {
  const ctx = useContext(SerialContext);
  if (!ctx) throw new Error("useSerial must be used inside SerialProvider");
  return ctx;
};
