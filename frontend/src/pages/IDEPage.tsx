// src/pages/IDEPage.tsx
import React, { useState, useEffect } from "react";
import { Layout, Typography, Card, Button, Space, Spin } from "antd";
import {
  PlayCircleOutlined,
  CodeOutlined,
  FileSearchOutlined,
  UploadOutlined,
} from "@ant-design/icons";
import Editor from "@monaco-editor/react";
import ModuleExplorer from "../components/ModuleExplorer";
import { useParams } from "react-router-dom";
import { usePywebviewApi } from "../hooks/usePywebviewApi";

const { Content, Sider } = Layout;
const { Title, Text } = Typography;

interface Project {
  project_id: string;
  name: string;
  description: string;
  is_active: boolean;
  updated_at: string;
  created_at: string;
  metadata?: Record<string, any>;
}

const IDEPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);

  const api = usePywebviewApi("get_project");

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

  useEffect(() => {
    const fetchProject = async () => {
      if (!api || !projectId) return;
      try {
        const result = await api.get_project(projectId);
        if (result && result.project_id) {
          setProject(result);
        } else {
          console.error("Invalid response from get_project:", result);
        }
      } catch (err) {
        console.error("❌ Error fetching project:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchProject();
  }, [api, projectId]);

  return (
    <Layout style={{ minHeight: "100vh", height: "100vh", overflow: "hidden" }}>
      <Layout style={{ height: "100%", overflow: "hidden" }}>
        {/* Module Explorer Sidebar */}
        <Sider
          width={400}
          theme="light"
          style={{
            borderRight: "1px solid #f0f0f0",
            background: "#fafafa",
            height: "100vh",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              padding: "12px 16px",
              borderBottom: "1px solid #f0f0f0",
              background: "#fff",
              flexShrink: 0,
            }}
          >
            <Title level={5} style={{ margin: 0 }}>
              <FileSearchOutlined style={{ marginRight: 8 }} />
              Module Explorer
            </Title>
            <Text type="secondary" style={{ fontSize: 12 }}>
              Search available functions, classes & variables
            </Text>
          </div>

          <div
            style={{
              height: "calc(100vh - 80px)",
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
            }}
          >
            <ModuleExplorer />
          </div>
        </Sider>

        {/* Main Editor Section */}
        <Layout
          style={{
            background: "#fff",
            height: "100vh",
            overflow: "hidden",
          }}
        >
          <Content
            style={{
              padding: "12px",
              height: "100%",
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
            }}
          >
            {/* Header with Title and Upload Button */}
            <Card
              style={{
                borderRadius: 8,
                boxShadow: "0 1px 8px rgba(0,0,0,0.06)",
                border: "1px solid #e8e8e8",
                marginBottom: 12,
                flexShrink: 0,
              }}
              bodyStyle={{ padding: "12px 16px" }}
            >
              {loading ? (
                <Spin size="small" />
              ) : (
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: "12px",
                  }}
                >
                  <div>
                    <Title level={5} style={{ margin: 0 }}>
                      <CodeOutlined
                        style={{ marginRight: 8, color: "#1890ff" }}
                      />
                      {project ? project.name : "Unknown Project"}
                    </Title>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {project
                        ? project.description
                        : "Write your Arduino-compatible Python code below"}
                    </Text>
                  </div>

                  <Button
                    type="primary"
                    icon={<PlayCircleOutlined />}
                    size="large"
                    style={{
                      borderRadius: 6,
                      padding: "0 24px",
                      height: "40px",
                      fontWeight: 600,
                      background:
                        "linear-gradient(135deg, #52c41a 0%, #73d13d 100%)",
                      border: "none",
                      boxShadow: "0 2px 4px rgba(82, 196, 26, 0.3)",
                    }}
                    onClick={() => {
                      if (window.pywebview?.api?.compile_project) {
                        window.pywebview.api.compile_project({ code });
                      } else {
                        console.log("Running code:", code);
                        alert(
                          "In a real environment, this would upload to Arduino"
                        );
                      }
                    }}
                  >
                    <Space>
                      <UploadOutlined />
                      Upload to Arduino
                    </Space>
                  </Button>
                </div>
              )}
            </Card>

            {/* Editor Section */}
            <Card
              style={{
                borderRadius: 8,
                boxShadow: "0 1px 8px rgba(0,0,0,0.06)",
                border: "1px solid #e8e8e8",
                flex: 1,
                display: "flex",
                flexDirection: "column",
                overflow: "hidden",
              }}
              bodyStyle={{
                padding: 0,
                flex: 1,
                display: "flex",
                flexDirection: "column",
                height: "100%",
              }}
            >
              <div
                style={{
                  flex: 1,
                  background: "#1e1e1e",
                  minHeight: 0,
                  position: "relative",
                }}
              >
                <Editor
                  height="100%"
                  defaultLanguage="python"
                  theme="vs-dark"
                  value={code}
                  onChange={(val) => setCode(val || "")}
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    fontFamily:
                      "'Fira Code', 'Cascadia Code', 'Monaco', 'Menlo', monospace",
                    automaticLayout: true,
                    scrollBeyondLastLine: false,
                    padding: { top: 16, bottom: 16 },
                    lineNumbersMinChars: 3,
                    folding: true,
                    glyphMargin: true,
                    renderLineHighlight: "all",
                    suggestOnTriggerCharacters: true,
                    wordBasedSuggestions: "matchingDocuments",
                    scrollbar: {
                      vertical: "visible",
                      horizontal: "visible",
                      useShadows: false,
                    },
                    quickSuggestions: true,
                    parameterHints: { enabled: true },
                    suggest: {
                      showFiles: false,
                      showStatusBar: false,
                    },
                  }}
                />

                {/* Editor Status Bar */}
                <div
                  style={{
                    position: "absolute",
                    bottom: 0,
                    left: 0,
                    right: 0,
                    background: "#007acc",
                    color: "white",
                    fontSize: "12px",
                    padding: "4px 12px",
                    display: "flex",
                    justifyContent: "space-between",
                  }}
                >
                  <span>Python</span>
                  <span>UTF-8</span>
                </div>
              </div>
            </Card>

            {/* Footer Info */}
            <div
              style={{
                padding: "8px 0",
                textAlign: "center",
                flexShrink: 0,
              }}
            >
              <Text type="secondary" style={{ fontSize: 12 }}>
                Ready to upload • Code length: {code.length} characters
              </Text>
            </div>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
};

export default IDEPage;
