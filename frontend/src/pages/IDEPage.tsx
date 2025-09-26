// src/pages/IDE.tsx
import React, { useState } from "react";
import { Layout, Menu, Typography, Card, Divider, List, Button, Space } from "antd";
import { PlayCircleOutlined, FileSearchOutlined, CodeOutlined } from "@ant-design/icons";
import Editor from "@monaco-editor/react";

const { Header, Content, Sider } = Layout;
const { Title, Text } = Typography;

const availableDocs = [
  {
    title: "Digital Write",
    description: "Set a pin HIGH or LOW. Example: digital_write(13, HIGH)",
  },
  {
    title: "Analog Read",
    description: "Read sensor values. Example: value = analog_read(A0)",
  },
  {
    title: "Delay",
    description: "Pause execution for X milliseconds. Example: delay(1000)",
  },
  {
    title: "Serial Print",
    description: "Print messages to Serial Monitor. Example: serial_print('Hello!')",
  },
];

const IDEPage: React.FC = () => {
  const [code, setCode] = useState<string>(
    `# Write your Python code here
def setup():
    serial_print("Setup complete")

def loop():
    digital_write(13, HIGH)
    delay(1000)
    digital_write(13, LOW)
    delay(1000)`
  );

  return (
    <Layout style={{ minHeight: "100vh" }}>
      {/* Header */}
      <Header
        style={{
          display: "flex",
          alignItems: "center",
          background: "#001529",
          color: "#fff",
          fontSize: "1.1rem",
          fontWeight: 500,
          padding: "0 24px",
        }}
      >
        <Space>
          <CodeOutlined />
          Mojoscale Python → Arduino IDE
        </Space>
      </Header>

      <Layout>
        {/* Documentation Panel */}
        <Sider
          width={320}
          theme="light"
          style={{ 
            borderRight: "1px solid #f0f0f0", 
            background: "#fafafa",
            boxShadow: "inset -1px 0 0 rgba(0,0,0,0.05)",
          }}
        >
          <div style={{ padding: "16px 16px 0 16px" }}>
            <Title level={4} style={{ marginBottom: 8 }}>
              <FileSearchOutlined style={{ marginRight: 8 }} />
              Documentation
            </Title>
            <Text type="secondary">Available functions for your Arduino</Text>
          </div>
          <Divider style={{ margin: "12px 0" }} />
          <List
            itemLayout="vertical"
            dataSource={availableDocs}
            style={{ padding: "0 16px 16px 16px" }}
            renderItem={(item) => (
              <List.Item style={{ padding: "8px 0" }}>
                <Card 
                  size="small" 
                  hoverable 
                  style={{ 
                    borderRadius: 8,
                    border: "1px solid #e8e8e8",
                    width: "100%",
                  }}
                  bodyStyle={{ padding: "12px" }}
                >
                  <Title level={5} style={{ marginBottom: 4, fontSize: "14px" }}>
                    {item.title}
                  </Title>
                  <Text type="secondary" style={{ fontSize: "12px" }}>
                    {item.description}
                  </Text>
                </Card>
              </List.Item>
            )}
          />
        </Sider>

        {/* Main Editor Section */}
        <Layout style={{ background: "#fff" }}>
          <Content style={{ padding: "24px" }}>
            <Card
              style={{
                borderRadius: 12,
                boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
                height: "calc(100vh - 120px)",
                display: "flex",
                flexDirection: "column",
                border: "1px solid #e8e8e8",
                overflow: "hidden",
              }}
              bodyStyle={{ 
                padding: "20px",
                flex: 1,
                display: "flex",
                flexDirection: "column",
                gap: "16px",
              }}
            >
              <div>
                <Title level={4} style={{ margin: 0 }}>
                  <CodeOutlined style={{ marginRight: 8 }} />
                  Python Code Editor
                </Title>
                <Text type="secondary">Write your Arduino-compatible Python code below</Text>
              </div>
              
              <Divider style={{ margin: 0 }} />

              {/* Editor Container with subtle border */}
              <div style={{ 
                flex: 1, 
                border: "1px solid #d9d9d9", 
                borderRadius: 8,
                overflow: "hidden",
                background: "#1e1e1e", // Match VS Dark theme background
              }}>
                <Editor
                  height="100%"
                  defaultLanguage="python"
                  theme="vs-dark"
                  value={code}
                  onChange={(val) => setCode(val || "")}
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    fontFamily: "'Fira Code', 'Cascadia Code', 'Monaco', 'Menlo', monospace",
                    automaticLayout: true,
                    scrollBeyondLastLine: false,
                    padding: { top: 16, bottom: 16 },
                    lineNumbersMinChars: 3,
                    folding: true,
                    glyphMargin: true,
                    renderLineHighlight: "all",
                    suggestOnTriggerCharacters: true,
                    wordBasedSuggestions: true,
                  }}
                />
              </div>

              <div style={{ 
                display: "flex", 
                justifyContent: "flex-end",
                paddingTop: "16px",
                borderTop: "1px solid #f0f0f0",
              }}>
                <Button
                  type="primary"
                  icon={<PlayCircleOutlined />}
                  size="large"
                  style={{
                    borderRadius: 6,
                    padding: "0 24px",
                    height: "40px",
                    fontWeight: 500,
                  }}
                  onClick={() => {
                    if (window.pywebview?.api?.compile_project) {
                      window.pywebview.api.compile_project({ code });
                    } else {
                      console.log("Running code:", code);
                      // Fallback for development
                      alert("In a real environment, this would upload to Arduino");
                    }
                  }}
                >
                  Upload to Arduino
                </Button>
              </div>
            </Card>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
};

export default IDEPage;