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

const { Text, Title } = Typography;

interface TerminalViewProps {
  onClose: () => void;
  onHeightChange: (height: number) => void;
}

export default function TerminalView({ onClose, onHeightChange }: TerminalViewProps) {
  const [lines, setLines] = useState<string[]>([
    "🚀 Mojoscale Terminal v1.0 - Serial Monitor",
    "📡 Connected to Arduino Uno on COM3",
    "⭐ Baud rate: 9600",
    "⏰ " + new Date().toLocaleTimeString() + " - Monitoring started...",
    ""
  ]);
  const [command, setCommand] = useState("");
  const [isMonitoring, setIsMonitoring] = useState(true);
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
  }, [lines]);

  // Simulate incoming serial data
  useEffect(() => {
    if (!isMonitoring) return;

    const interval = setInterval(() => {
      const messages = [
        "📊 Sensor reading: 25.3°C",
        "💡 LED toggled: PIN 13 → HIGH",
        "📈 Analog input A0: 512",
        "🔄 Loop iteration completed",
        "📡 Ping from device: OK"
      ];
      
      if (Math.random() > 0.7) {
        setLines(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${messages[Math.floor(Math.random() * messages.length)]}`]);
        setLineCount(prev => prev + 1);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [isMonitoring]);

  // Drag to resize functionality - FIXED VERSION
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing.current) return;
      
      const deltaY = startY.current - e.clientY;
      const newHeight = Math.max(200, Math.min(700, startHeight.current + deltaY));
      onHeightChange(newHeight);
    };

    const handleMouseUp = () => {
      isResizing.current = false;
      document.body.style.cursor = 'default';
      document.body.style.userSelect = 'auto';
    };

    const handleMouseDown = (e: MouseEvent) => {
      e.preventDefault();
      isResizing.current = true;
      startY.current = e.clientY;
      startHeight.current = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--terminal-height') || '300');
      document.body.style.cursor = 'row-resize';
      document.body.style.userSelect = 'none';
    };

    const resizeElement = resizeRef.current;
    if (resizeElement) {
      resizeElement.addEventListener('mousedown', handleMouseDown);
    }

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      if (resizeElement) {
        resizeElement.removeEventListener('mousedown', handleMouseDown);
      }
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [onHeightChange]);

  const handleEnter = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && command.trim()) {
      const newLines = [
        `> ${command}`,
        `✅ Command executed successfully`,
        `📤 Sent: ${command.length} bytes`
      ];
      setLines(prev => [...prev, ...newLines]);
      setLineCount(prev => prev + 3);
      setCommand("");
    }
  };

  const clearTerminal = () => {
    setLines(["🗑️ Terminal cleared", "⏰ " + new Date().toLocaleTimeString() + " - Monitoring " + (isMonitoring ? "resumed" : "paused")]);
    setLineCount(0);
  };

  const toggleMonitoring = () => {
    setIsMonitoring(!isMonitoring);
    setLines(prev => [...prev, `⏸️ Monitoring ${!isMonitoring ? "started" : "paused"}`]);
  };

  const downloadLogs = () => {
    const logContent = lines.join('\n');
    const blob = new Blob([logContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `serial-monitor-${new Date().toISOString().split('T')[0]}.log`;
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
        height: "100%"
      }}
    >
      {/* Resize Handle - Made more prominent */}
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
          transition: "all 0.2s ease",
          borderTop: "2px solid rgba(255,255,255,0.3)",
        }}
        onMouseEnter={() => {
          if (resizeRef.current) {
            resizeRef.current.style.opacity = '1';
            resizeRef.current.style.height = '16px';
          }
        }}
        onMouseLeave={() => {
          if (resizeRef.current && !isResizing.current) {
            resizeRef.current.style.opacity = '0.9';
            resizeRef.current.style.height = '12px';
          }
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
      }}>
        <Space>
          <UsbOutlined style={{ color: "white", fontSize: "16px" }} />
          <Title level={5} style={{ color: "white", margin: 0 }}>
            Serial Monitor
          </Title>
        </Space>
        <Space>
          <Text style={{ color: "rgba(255,255,255,0.8)", fontSize: "12px" }}>
            📈 {lineCount} lines • {isMonitoring ? "🟢 Live" : "⏸️ Paused"}
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

      {/* Terminal Content */}
      <div
        ref={terminalRef}
        style={{
          flex: 1,
          overflowY: "auto",
          fontFamily: "'Fira Code', 'Cascadia Code', monospace",
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
        }}
      >
        {lines.map((line, idx) => (
          <Text 
            key={idx} 
            style={{ 
              display: "block", 
              color: line.startsWith(">") ? "#ffa500" : 
                     line.startsWith("✅") ? "#00ff00" : 
                     line.startsWith("📤") ? "#00ffff" : 
                     line.startsWith("⏰") ? "#ff6b6b" : "#00ff00",
              textShadow: "0 0 1px currentColor",
              marginBottom: "2px",
              wordBreak: "break-word",
            }}
          >
            {line}
          </Text>
        ))}
        <div style={{ 
          color: "#00ff00", 
          opacity: 0.7, 
          textAlign: "center",
          marginTop: "20px",
          fontSize: "11px",
        }}>
          {isMonitoring ? "● Live monitoring..." : "⏸️ Monitoring paused"}
        </div>
      </div>

      {/* Control Bar */}
      <div style={{
        padding: "12px 16px",
        background: "rgba(0, 0, 0, 0.3)",
        borderTop: "1px solid #333",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}>
        <Space>
          <Button
            type="primary"
            size="small"
            icon={isMonitoring ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
            onClick={toggleMonitoring}
            style={{
              background: isMonitoring ? "#faad14" : "#52c41a",
              border: "none",
              borderRadius: "6px"
            }}
          >
            {isMonitoring ? "Pause" : "Resume"}
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