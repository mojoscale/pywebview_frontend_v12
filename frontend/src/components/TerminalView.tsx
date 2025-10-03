import { useState, useRef, useEffect } from "react";
import { Card, Typography, Input, Button, Space } from "antd";
import { 
  PlayCircleOutlined, 
  PauseCircleOutlined, 
  ClearOutlined, 
  DownloadOutlined,
  UsbOutlined,
  DragOutlined,
  CloseOutlined
} from "@ant-design/icons";
import { useSerial } from "../contexts/SerialContext";

const { Text, Title } = Typography;

interface TerminalViewProps {
  onClose: () => void;
  onHeightChange: (height: number) => void;
}

export default function TerminalView({ onClose, onHeightChange }: TerminalViewProps) {
  const { terminalLogs, clearTerminal, serialConnected, monitoring } = useSerial();

  const [command, setCommand] = useState("");
  const [lineCount, setLineCount] = useState(0);
  const terminalRef = useRef<HTMLDivElement>(null);
  const resizeRef = useRef<HTMLDivElement>(null);
  const isResizing = useRef(false);
  const startY = useRef(0);
  const startHeight = useRef(300);

  // Auto-scroll to bottom when new lines are added
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
    setLineCount(terminalLogs.length);
  }, [terminalLogs]);

  // Drag to resize
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

  const handleEnter = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && command.trim()) {
      // In a real implementation, you would send the command to the serial device
      // For now, we'll just add it to the logs for demonstration
      const newLogs = [
        `> ${command}`,
        `✅ Command sent to device`,
        `📤 Sent: ${command.length} bytes`
      ];
      // Note: You might want to use a proper state update here
      // This is just for demonstration
      newLogs.forEach(line => {
        // This would ideally be handled by your serial context
        console.log("Command:", line);
      });
      setCommand("");
    }
  };

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

  const toggleMonitoring = () => {
    // This would toggle monitoring in your serial context
    console.log("Toggle monitoring");
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
        overflow: "hidden" // Important: Prevent card body from scrolling
      }}
    >
      {/* Resize Handle */}
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
          flexShrink: 0, // Prevent resize handle from shrinking
        }}
      >
        <DragOutlined style={{ color: "white", fontSize: "16px" }} />
        <div style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          color: "white",
          fontSize: "10px",
          fontWeight: "bold",
          textShadow: "0 1px 2px rgba(0,0,0,0.5)"
        }}>
          DRAG TO RESIZE
        </div>
      </div>

      {/* Header */}
      <div style={{
        background: "linear-gradient(135deg, #1890ff 0%, #096dd9 100%)",
        padding: "12px 16px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        borderBottom: "1px solid #333",
        flexShrink: 0, // Prevent header from shrinking
      }}>
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

      {/* Terminal Content - This is the scrollable section */}
      <div
        ref={terminalRef}
        style={{
          flex: 1,
          overflowY: "auto",
          overflowX: "hidden",
          fontFamily: "'Fira Code', 'Cascadia Code', 'Monaco', 'Consolas', monospace",
          fontSize: "13px",
          lineHeight: "1.4",
          whiteSpace: "pre-wrap",
          color: "#00ff00",
          padding: "16px",
          background: "#000",
          backgroundImage: `
            radial-gradient(circle at 25% 25%, #0a0a0a 0%, transparent 50%),
            radial-gradient(circle at 75% 75%, #0a0a0a 0%, transparent 50%)
          `,
          margin: "12px",
          borderRadius: "8px",
          boxShadow: "inset 0 0 20px rgba(0, 255, 0, 0.1)",
          wordBreak: "break-word",
          minHeight: 0, // Important for flex child scrolling
        }}
      >
        {terminalLogs.length === 0 ? (
          <div style={{ 
            color: "#666", 
            textAlign: "center", 
            padding: "20px",
            fontStyle: "italic" 
          }}>
            No terminal output yet. Connect to a device to see serial data.
          </div>
        ) : (
          terminalLogs.map((line, idx) => (
            <div
              key={idx}
              style={{
                color: line.startsWith(">") ? "#ffa500" :
                       line.startsWith("✅") ? "#00ff00" :
                       line.startsWith("❌") ? "#ff4444" :
                       line.startsWith("⚠️") ? "#ffaa00" :
                       line.startsWith("📤") ? "#00ffff" :
                       line.startsWith("🔧") ? "#a855f7" :
                       line.startsWith("🚀") ? "#00ff88" : 
                       line.startsWith("📦") ? "#ffa500" : "#00ff00",
                textShadow: "0 0 1px currentColor",
                marginBottom: "4px",
                wordBreak: "break-word",
                display: "block",
              }}
            >
              {line}
            </div>
          ))
        )}
        
        {/* Scroll indicator */}
        {terminalLogs.length > 20 && (
          <div style={{ 
            color: "#666", 
            fontSize: "11px", 
            textAlign: "center",
            marginTop: "10px",
            padding: "4px",
            borderTop: "1px solid #333",
            opacity: 0.7
          }}>
            Scroll to see more... ({terminalLogs.length} lines)
          </div>
        )}
      </div>

      {/* Control Bar */}
      <div style={{
        padding: "12px 16px",
        background: "rgba(0, 0, 0, 0.3)",
        borderTop: "1px solid #333",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexShrink: 0, // Prevent control bar from shrinking
      }}>
        <Space>
          <Button
            type="primary"
            size="small"
            icon={monitoring ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
            onClick={toggleMonitoring}
            style={{
              background: monitoring ? "#faad14" : "#52c41a",
              border: "none",
              borderRadius: "6px"
            }}
          >
            {monitoring ? "Pause" : "Resume"}
          </Button>
          
          <Button
            size="small"
            icon={<ClearOutlined />}
            onClick={clearTerminal}
            style={{
              background: "#ff4d4f",
              color: "white",
              border: "none",
              borderRadius: "6px"
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
              borderRadius: "6px"
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
          prefix={<Text style={{ color: "#00ff00", fontFamily: "monospace" }}></Text>}
        />
      </div>
    </Card>
  );
}