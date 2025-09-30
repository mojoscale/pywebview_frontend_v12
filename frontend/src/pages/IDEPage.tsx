// src/pages/IDEPage.tsx
import React, { useState, useEffect, useRef, useCallback } from "react";
import { Layout, Typography, Card, Button, Space, Spin, List } from "antd";
import {
  PlayCircleOutlined,
  CodeOutlined,
  FileSearchOutlined,
  UploadOutlined,
  BugOutlined,
} from "@ant-design/icons";
import MonacoEditor from "@monaco-editor/react";
import type * as monaco from "monaco-editor";
import ModuleExplorer from "../components/ModuleExplorer";
import { useParams } from "react-router-dom";

const { Content, Sider } = Layout;
const { Title, Text } = Typography;

interface Project {
  project_id: string;
  name: string;
  description: string;
  is_active: boolean;
  updated_at: string;
  created_at: string;
  metadata?: {
    platform?: string;
    [key: string]: any;
  };
}

const IDEPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState<any[]>([]);
  const [isApiReady, setIsApiReady] = useState(false);

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

  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<typeof monaco | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // ✅ Wait for pywebview API to be ready
  useEffect(() => {
    const checkApiReady = () => {
      if (window.pywebview?.api) {
        setIsApiReady(true);
        return true;
      }
      return false;
    };

    if (checkApiReady()) {
      return;
    }

    const handleReady = () => {
      if (checkApiReady()) {
        console.log("pywebview API ready in IDEPage");
      }
    };

    window.addEventListener('pywebviewready', handleReady);

    const interval = setInterval(() => {
      if (checkApiReady()) {
        clearInterval(interval);
      }
    }, 100);

    const timeoutId = setTimeout(() => {
      clearInterval(interval);
      console.warn("pywebview API not available in IDEPage");
    }, 5000);

    return () => {
      clearInterval(interval);
      clearTimeout(timeoutId);
      window.removeEventListener('pywebviewready', handleReady);
    };
  }, []);

  // Fetch project when API is ready
  useEffect(() => {
    const fetchProject = async () => {
      if (!isApiReady || !projectId) return;
      
      try {
        if (!window.pywebview?.api) return;
        const result = await window.pywebview.api.get_project(projectId);
        if (result?.project_id) {
          setProject(result);
        }
      } catch (err) {
        console.error("❌ Error fetching project:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchProject();
  }, [isApiReady, projectId]);

  // Handle linting with debouncing
  const lintCode = useCallback(
    async (currentCode: string) => {
      if (!monacoRef.current || !editorRef.current || !isApiReady) {
        console.warn("Editor, Monaco, or API not ready");
        return;
      }

      try {
        const board = project?.metadata?.platform || "arduino";
        console.log("🔍 Running lint for platform:", board);

        if (!window.pywebview?.api) return;
        const result = await window.pywebview.api.lint_code(currentCode, board);

        if (!result || !Array.isArray(result.errors)) {
          console.warn("[WARN] lint_code returned invalid result:", result);
          setErrors([]);
          return;
        }

        const model = editorRef.current.getModel();
        if (!model) return;

        const markers = result.errors.map((err) => ({
          startLineNumber: err.line,
          endLineNumber: err.line,
          startColumn: err.column || 1,
          endColumn: err.column
            ? err.column + 1
            : model.getLineMaxColumn(err.line),
          message: err.message,
          severity: monacoRef.current!.MarkerSeverity.Error,
        }));

        monacoRef.current!.editor.setModelMarkers(model, "python-linter", markers);
        setErrors(result.errors);
        console.log("✅ Lint completed. Found", result.errors.length, "errors");
      } catch (e) {
        console.error("[ERROR] Exception during linting:", e);
        setErrors([]);
      }
    },
    [project, isApiReady]
  );

  // Debounced lint effect
  useEffect(() => {
    if (!project || !editorRef.current || !isApiReady) return;

    const timeoutId = setTimeout(() => {
      console.log("🚀 Running initial lint on startup");
      lintCode(editorRef.current?.getValue() || "");
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [project, lintCode, isApiReady]);

  // Editor mount
  const handleEditorDidMount = (
    editor: monaco.editor.IStandaloneCodeEditor,
    monacoInstance: typeof monaco
  ) => {
    editorRef.current = editor;
    monacoRef.current = monacoInstance;

    // Throttle content changes to reduce memory usage
    //let changeTimeout: NodeJS.Timeout;
    let changeTimeout: ReturnType<typeof setTimeout>;
    editor.onDidChangeModelContent(() => {
      clearTimeout(changeTimeout);
      changeTimeout = setTimeout(() => {
        const currentCode = editor.getValue();
        setCode(currentCode);
      }, 300);
    });

    console.log("✅ Editor mounted");
  };

  // Cleanup on unmount to free memory
  useEffect(() => {
    return () => {
      if (editorRef.current) {
        const model = editorRef.current.getModel();
        if (model) {
          model.dispose();
        }
        editorRef.current.dispose();
        editorRef.current = null;
      }
      monacoRef.current = null;
    };
  }, []);

  // Manual lint trigger
  const handleManualLint = () => {
    console.log("🔄 Manual lint triggered");
    if (editorRef.current && isApiReady) {
      lintCode(editorRef.current.getValue());
    }
  };

  const handleUploadToArduino = () => {
  if (!window.pywebview?.api) return;

  if (isApiReady && window.pywebview.api.compile_project) {
    window.pywebview.api.compile_project({
      projectId: project?.project_id || "",  // <-- include projectId
      code,
      platform: project?.metadata?.platform || "arduino",
    });
  } else {
    alert("In a real environment, this would upload to Arduino");
  }
};

  // Show loading while waiting for API
  if (!isApiReady) {
    return (
      <Layout style={{ minHeight: "100vh", display: "flex", justifyContent: "center", alignItems: "center" }}>
        <Spin size="large" tip="Initializing IDE..." />
      </Layout>
    );
  }

  return (
    <Layout style={{ minHeight: "100vh", overflow: "hidden" }}>
      <Layout>
        {/* Sidebar */}
        <Sider width={400} theme="light">
          <div style={{ padding: "12px 16px", borderBottom: "1px solid #f0f0f0" }}>
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
              display: "flex",
              flexDirection: "column",
            }}
          >
            <ModuleExplorer />
          </div>
        </Sider>

        {/* Main Section */}
        <Layout style={{ background: "#fff" }}>
          <Content style={{ padding: "12px", display: "flex", flexDirection: "column", height: "100vh" }}>
            {/* Header */}
            <Card 
              size="small" 
              style={{ marginBottom: 12 }}
              bodyStyle={{ padding: "12px" }}
            >
              {loading ? (
                <Spin size="small" />
              ) : (
                <div style={{ display: "flex", justifyContent: "space-between", gap: "12px", alignItems: "flex-start" }}>
                  <div style={{ flex: 1 }}>
                    <Title level={5} style={{ margin: 0, lineHeight: 1.2 }}>
                      <CodeOutlined style={{ marginRight: 8, color: "#1890ff" }} />
                      {project ? project.name : "Unknown Project"}
                    </Title>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {project?.description ||
                        "Write your Arduino-compatible Python code below"}
                    </Text>
                  </div>
                  <Space>
                    <Button
                      size="small"
                      icon={<BugOutlined />}
                      onClick={handleManualLint}
                      style={{ borderRadius: 6 }}
                    >
                      Run Lint
                    </Button>
                    <Button
                      size="small"
                      type="primary"
                      icon={<PlayCircleOutlined />}
                      onClick={handleUploadToArduino}
                    >
                      <Space size={4}>
                        <UploadOutlined />
                        Upload to Arduino
                      </Space>
                    </Button>
                  </Space>
                </div>
              )}
            </Card>

            {/* Editor Container */}
            <Card 
              style={{ 
                flex: 1, 
                display: "flex", 
                flexDirection: "column",
                padding: 0,
                overflow: "hidden"
              }}
              bodyStyle={{ 
                padding: 0, 
                flex: 1, 
                display: "flex", 
                flexDirection: "column",
                overflow: "hidden"
              }}
            >
              <div 
                ref={containerRef}
                style={{ 
                  flex: 1, 
                  minHeight: 0,
                  position: "relative",
                  overflow: "hidden"
                }}
              >
                <MonacoEditor
                  language="python"
                  value={code}
                  theme="vs-dark"
                  onMount={handleEditorDidMount}
                  onChange={(val) => setCode(val || "")}
                  height="100%"
                  options={{
                    fontSize: 14,
                    minimap: { enabled: false },
                    scrollBeyondLastLine: false,
                    automaticLayout: true,
                    glyphMargin: false,
                    contextmenu: false,
                    //lightbulb: { enabled: false },
                    renderValidationDecorations: "on",
                    lineNumbersMinChars: 3,
                    folding: false,
                    occurrencesHighlight: "off",
                    selectionHighlight: false,
                    suggestOnTriggerCharacters: false,
                    wordBasedSuggestions: "off",
                    parameterHints: { enabled: false },
                  }}
                />
              </div>

              {/* Problems panel */}
              {errors.length > 0 && (
                <List
                  size="small"
                  bordered
                  dataSource={errors}
                  style={{ 
                    marginTop: 8, 
                    maxHeight: 120, 
                    overflow: "auto",
                    flexShrink: 0
                  }}
                  renderItem={(err: any) => (
                    <List.Item
                      onClick={() => {
                        editorRef.current?.revealLineInCenter(err.line);
                        editorRef.current?.setPosition({
                          lineNumber: err.line,
                          column: err.column || 1,
                        });
                        editorRef.current?.focus();
                      }}
                      style={{ 
                        cursor: "pointer",
                        padding: "4px 12px" 
                      }}
                    >
                      <Text type="danger" style={{ fontSize: 12 }}>
                        Line {err.line}, Col {err.column || 1}: {err.message}
                      </Text>
                    </List.Item>
                  )}
                />
              )}
            </Card>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
};

export default IDEPage;