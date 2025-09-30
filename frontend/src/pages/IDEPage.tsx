// src/pages/IDEPage.tsx
import React, { useState, useEffect, useRef, useCallback } from "react";
import { Layout, Typography, Card, Button, Space, Spin, List } from "antd";
import {
  PlayCircleOutlined,
  CodeOutlined,
  FileSearchOutlined,
  UploadOutlined,
} from "@ant-design/icons";
import MonacoEditor from "@monaco-editor/react";
import * as monaco from "monaco-editor";
import type { OnMount } from "@monaco-editor/react";

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

  const api = usePywebviewApi();

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
  const debounceRef = useRef<NodeJS.Timeout | null>(null);
  const completionProviderRef = useRef<monaco.IDisposable | null>(null);

  // Fetch project
  useEffect(() => {
    const fetchProject = async () => {
      if (!api || !projectId) return;
      try {
        const result = await api.get_project(projectId);
        if (result && result.project_id) {
          setProject(result);
        }
      } catch (err) {
        console.error("❌ Error fetching project:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchProject();
  }, [api, projectId]);

  // Handle linting
  const lintCode = useCallback(
    async (currentCode: string) => {
      if (!monacoRef.current || !editorRef.current) return;
      try {
        const board = project?.metadata?.platform || "arduino";
        const result = await window.pywebview?.api?.lint_code(currentCode, board);

        if (!result || !Array.isArray(result.errors)) {
          console.warn("[WARN] lint_code returned invalid result:", result);
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
          severity: monaco.MarkerSeverity.Error,
        }));

        monacoRef.current.editor.setModelMarkers(model, "python-linter", markers);
        setErrors(result.errors);
      } catch (e) {
        console.error("[ERROR] Exception during linting:", e);
      }
    },
    [project]
  );

  // Handle editor mount
  const handleEditorDidMount: OnMount = (editor, monacoInstance) => {
    editorRef.current = editor;
    monacoRef.current = monacoInstance;

    // Register completions once
    if (!completionProviderRef.current) {
      completionProviderRef.current =
        monacoInstance.languages.registerCompletionItemProvider("python", {
          triggerCharacters: [".", "(", "[", '"', "'", " "],
          provideCompletionItems: async (model, position) => {
            const code = model.getValue();
            const line = position.lineNumber - 1;
            const column = position.column - 1;
            try {
              const response = await window.pywebview?.api?.get_completions(
                code,
                line,
                column
              );
              if (!Array.isArray(response)) return { suggestions: [] };
              return {
                suggestions: response.map((item) => ({
                  label: item.label,
                  kind: monacoInstance.languages.CompletionItemKind.Function,
                  insertText: item.insertText || item.label,
                  documentation: item.documentation,
                  detail: item.detail,
                  range: new monaco.Range(
                    position.lineNumber,
                    position.column,
                    position.lineNumber,
                    position.column
                  ),
                })),
              };
            } catch {
              return { suggestions: [] };
            }
          },
        });
    }

    // Debounced lint on change
    editor.onDidChangeModelContent(() => {
      const currentCode = editor.getValue();
      setCode(currentCode);

      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => lintCode(currentCode), 500);
    });

    // Initial lint
    lintCode(editor.getValue());
  };

  const handleUploadToArduino = () => {
    if (api?.compile_project) {
      api.compile_project({
        code,
        platform: project?.metadata?.platform || "arduino",
      });
    } else {
      alert("In a real environment, this would upload to Arduino");
    }
  };

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
          <div style={{ height: "calc(100vh - 80px)", display: "flex", flexDirection: "column" }}>
            <ModuleExplorer />
          </div>
        </Sider>

        {/* Main Section */}
        <Layout style={{ background: "#fff" }}>
          <Content style={{ padding: "12px", display: "flex", flexDirection: "column" }}>
            {/* Header */}
            <Card style={{ marginBottom: 12 }}>
              {loading ? (
                <Spin size="small" />
              ) : (
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <div>
                    <Title level={5}>
                      <CodeOutlined style={{ marginRight: 8, color: "#1890ff" }} />
                      {project ? project.name : "Unknown Project"}
                    </Title>
                    <Text type="secondary">
                      {project?.description || "Write your Arduino-compatible Python code below"}
                    </Text>
                  </div>
                  <Button
                    type="primary"
                    icon={<PlayCircleOutlined />}
                    onClick={handleUploadToArduino}
                  >
                    <Space>
                      <UploadOutlined />
                      Upload to Arduino
                    </Space>
                  </Button>
                </div>
              )}
            </Card>

            {/* Editor */}
            <Card style={{ flex: 1, display: "flex", flexDirection: "column" }}>
              <MonacoEditor
                language="python"
                value={code}
                theme="vs-dark"
                onMount={handleEditorDidMount}
                onChange={(val) => setCode(val || "")}
                options={{
                  fontSize: 14,
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  glyphMargin: true,
                  renderValidationDecorations: "on",
                }}
              />

              {/* Problems panel */}
              {errors.length > 0 && (
                <List
                  size="small"
                  bordered
                  dataSource={errors}
                  style={{ marginTop: 8, maxHeight: 120, overflow: "auto" }}
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
                      style={{ cursor: "pointer" }}
                    >
                      <Text type="danger">
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
