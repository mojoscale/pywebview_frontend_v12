import { useState } from "react";
import { Card, Typography, Input } from "antd";

const { Text } = Typography;

export default function TerminalView() {
  const [lines, setLines] = useState<string[]>([
    "Welcome to Mojoscale Terminal!",
    "Type your commands below..."
  ]);
  const [command, setCommand] = useState("");

  const handleEnter = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && command.trim()) {
      setLines((prev) => [...prev, `> ${command}`, `Executed: ${command}`]);
      setCommand("");
    }
  };

  return (
    <Card
      style={{
        background: "#111",
        color: "#0f0",
        borderRadius: "12px",
        boxShadow: "0 4px 12px rgba(0,0,0,0.4)",
        height: "400px",
        display: "flex",
        flexDirection: "column",
      }}
      bodyStyle={{ padding: "12px", display: "flex", flexDirection: "column", flex: 1 }}
    >
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          fontFamily: "monospace",
          fontSize: "14px",
          lineHeight: "1.4",
          whiteSpace: "pre-wrap",
          color: "#0f0",
        }}
      >
        {lines.map((line, idx) => (
          <Text key={idx} style={{ display: "block", color: "#0f0" }}>
            {line}
          </Text>
        ))}
      </div>
      <Input
        placeholder="Type a command..."
        value={command}
        onChange={(e) => setCommand(e.target.value)}
        onKeyDown={handleEnter}
        style={{
          marginTop: "8px",
          background: "black",
          color: "#0f0",
          fontFamily: "monospace",
        }}
      />
    </Card>
  );
}
