import { useState, useRef, useEffect } from "react";
import { Card, Typography, Input, Button, Space } from "antd";
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  ClearOutlined,
  DownloadOutlined,
  UsbOutlined,
  DragOutlined,
  CloseOutlined,
} from "@ant-design/icons";

const { Text, Title } = Typography;

interface TerminalViewProps {
  onClose: () => void;
  onHeightChange: (height: number) => void;
}

export default function TerminalView({ onClose, onHeightChange }: TerminalViewProps) {
  const [terminalLogs, setTerminalLogs] = useState<string[]>([]);
  const [command, setCommand] = useState("");
  const [lineCount, setLineCount] = useState(0);
  const [monitoring, setMonitoring] = useState(false);
  const [serialConnected, setSerialConnected] = useState(false);

  const terminalRef = useRef<HTMLDivElement>(null);
  const resizeRef = useRef<HTMLDivElement>(null);
  const isResizing = useRef(false);
  const startY = useRef(0);
  const startHeight = useRef(300);

  // 🔹 Listen for serial-log events from backend
  useEffect(() => {
    const handleSerialLog = (event: CustomEvent) => {
      setTerminalLogs((prev) => [...prev, event.detail]);
    };

    window.addEventListener("serial-log", handleSerialLog as EventListener);
    return () => window.removeEventListener("serial-log", handleSerialLog as EventListener);
  }, []);

  // 🔹 Auto-scroll when new lines arrive
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
    setLineCount(terminalLogs.length);
  }, [terminalLogs]);

  // 🔹 Drag to resize terminal panel
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing.current) return;
      const deltaY = startY.current - e.clientY;
      const newHeight = Math.max(200, Math.min(700, startHeight.current + deltaY));
      onHeightChange(newHeight);
    };

    const handleMouseUp = () => {
      isResizing.current = false;
      document.body.style.cursor = "default";
      document.body.style.userSelect = "auto";
    };

    const handleMouseDown = (e: MouseEvent) => {
      e.preventDefault();
      isResizing.current = true;
      startY.current = e.clientY;
      startHeight.current = parseInt(
        getComputedStyle(document.documentElement).getPropertyValue("--terminal-height") || "300"
      );
      document.body.style.cursor = "row-resize";
      document.body.style.userSelect = "none";
    };

    const resizeElement = resizeRef.current;
    if (resizeElement) resizeElement.addEventListener("mousedown", handleMouseDown);

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);

    return () => {
      if (resizeElement) resizeElement.removeEventListener("mousedown", handleMouseDown);
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [onHeightChange]);

  // 🔹 Send command to backend
  const handleEnter = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && command.trim()) {
      setTerminalLogs((prev) => [...prev, `> ${command}`]);
      try {
        const res = await window.pywebview.api.send_serial_command(command);
        if (res.status === "ok") {
          setTerminalLogs((prev) => [...prev, `📤 Sent ${res.sent} bytes`]);
        } else {
          setTerminalLogs((prev) => [...prev, `❌ ${res.message || "Error sending command"}`]);
        }
      } catch (err: any) {
        setTerminalLogs((prev) => [...prev, `❌ ${err.message || err}`]);
      }
      setCommand("");
    }
  };

  // 🔹 Start/stop monitoring
  const toggleMonitoring = async () => {
    try {
      if (monitoring) {
        const res = await window.pywebview.api.stop_serial_monitor();
        if (res.status === "stopped") {
          setMonitoring(false);
          setSerialConnected(false);
          setTerminalLogs((prev) => [...prev, "🛑 Monitoring stopped"]);
        }
      } else {
        const res = await window.pywebview.api.start_serial_monitor();
        if (res.status === "connected") {
          setMonitoring(true);
          setSerialConnected(true);
          setTerminalLogs((prev) => [...prev, `🚀 Connected to ${res.port}`]);
        } else {
          setTerminalLogs((prev) => [...prev, `❌ ${res.message || "Connection failed"}`]);
        }
      }
    } catch (err: any) {
      setTerminalLogs((prev) => [...prev, `❌ ${err.message || err}`]);
    }
  };

  // 🔹 Clear terminal
  const clearTerminal = () => {
    setTerminalLogs([]);
  };

  // 🔹 Export logs
  const downloadLogs = () => {
    const logContent = terminalLogs.join("\n");
    const blob = new Blob([logContent], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `serial-monitor-${new Date().toISOString().split("T")[0]}.log`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Card
      style={{
        background: "linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)",
        borderRadius: "12px 12px 0 0",
        boxShadow: "0 -4px 20px rgba(0,0,0,0.4)",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        border: "1px solid #333",
        borderBottom: "none",
      }}
      bodyStyle={{
        padding: "0",
        display: "flex",
        flexDirection: "column",
        flex: 1,
        height: "100%",
        overflow: "hidden",
      }}
    >
      {/* Resize handle */}
      <div
        ref={resizeRef}
        style={{
          height: "12px",
          background: "linear-gradient(90deg, #1890ff 0%, #52c41a 50%, #faad14 100%)",
          cursor: "row-resize",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          position: "relative",
          opacity: 0.9,
          borderTop: "2px solid rgba(255,255,255,0.3)",
          flexShrink: 0,
        }}
      >
        <DragOutlined style={{ color: "white", fontSize: "16px" }} />
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            color: "white",
            fontSize: "10px",
            fontWeight: "bold",
            textShadow: "0 1px 2px rgba(0,0,0,0.5)",
          }}
        >
          DRAG TO RESIZE
        </div>
      </div>

      {/* Header */}
      <div
        style={{
          background: "linear-gradient(135deg, #1890ff 0%, #096dd9 100%)",
          padding: "12px 16px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderBottom: "1px solid #333",
          flexShrink: 0,
        }}
      >
        <Space>
          <UsbOutlined style={{ color: "white", fontSize: "16px" }} />
          <Title level={5} style={{ color: "white", margin: 0 }}>
            Serial Monitor
          </Title>
        </Space>
        <Space>
          <Text style={{ color: "rgba(255,255,255,0.8)", fontSize: "12px" }}>
            📈 {lineCount} lines • {serialConnected ? "🟢 Connected" : "🔴 Disconnected"}
          </Text>
          <Button
            type="text"
            icon={<CloseOutlined />}
            onClick={onClose}
            style={{ color: "white" }}
            size="small"
          />
        </Space>
      </div>

      {/* Terminal log area */}
      <div
        ref={terminalRef}
        style={{
          flex: 1,
          overflowY: "auto",
          fontFamily: "'Fira Code', monospace",
          fontSize: "13px",
          lineHeight: "1.4",
          whiteSpace: "pre-wrap",
          color: "#00ff00",
          padding: "16px",
          background: "#000",
          margin: "12px",
          borderRadius: "8px",
          boxShadow: "inset 0 0 20px rgba(0, 255, 0, 0.1)",
        }}
      >
        {terminalLogs.length === 0 ? (
          <div
            style={{ color: "#666", textAlign: "center", padding: "20px", fontStyle: "italic" }}
          >
            No terminal output yet. Start monitoring to view serial data.
          </div>
        ) : (
          terminalLogs.map((line, idx) => (
            <div
              key={idx}
              style={{
                color: line.startsWith(">") ? "#ffa500" :
                       line.startsWith("✅") ? "#00ff00" :
                       line.startsWith("❌") ? "#ff4444" :
                       line.startsWith("📤") ? "#00ffff" :
                       line.startsWith("🛑") ? "#ffaa00" :
                       line.startsWith("🚀") ? "#00ff88" : "#00ff00",
                marginBottom: "4px",
              }}
            >
              {line}
            </div>
          ))
        )}
      </div>

      {/* Footer / Controls */}
      <div
        style={{
          padding: "12px 16px",
          background: "rgba(0, 0, 0, 0.3)",
          borderTop: "1px solid #333",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexShrink: 0,
        }}
      >
        <Space>
          <Button
            type="primary"
            size="small"
            icon={monitoring ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
            onClick={toggleMonitoring}
            style={{
              background: monitoring ? "#faad14" : "#52c41a",
              border: "none",
              borderRadius: "6px",
            }}
          >
            {monitoring ? "Stop" : "Start"}
          </Button>

          <Button
            size="small"
            icon={<ClearOutlined />}
            onClick={clearTerminal}
            style={{
              background: "#ff4d4f",
              color: "white",
              border: "none",
              borderRadius: "6px",
            }}
          >
            Clear
          </Button>

          <Button
            size="small"
            icon={<DownloadOutlined />}
            onClick={downloadLogs}
            style={{
              background: "#1890ff",
              color: "white",
              border: "none",
              borderRadius: "6px",
            }}
          >
            Export
          </Button>
        </Space>

        <Input
          placeholder="Type command and press Enter..."
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          onKeyDown={handleEnter}
          style={{
            width: "300px",
            background: "rgba(0, 0, 0, 0.7)",
            color: "#00ff00",
            fontFamily: "'Fira Code', monospace",
            border: "1px solid #333",
            borderRadius: "6px",
            padding: "6px 12px",
          }}
        />
      </div>
    </Card>
  );
}
