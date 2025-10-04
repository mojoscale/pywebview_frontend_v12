// src/pages/IDEPage.tsx
import React, { useState, useEffect, useRef, useCallback } from "react";
import { Layout, Typography, Card, Button, Space, Spin, List, message } from "antd";
import {
  PlayCircleOutlined,
  CodeOutlined,
  FileSearchOutlined,
  UploadOutlined,
  BugOutlined,
  SaveOutlined,
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

interface CompletionItem {
  label: string;
  kind: number;
  insertText?: string;
  documentation?: string;
  detail?: string;
}

const IDEPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState<any[]>([]);
  const [isApiReady, setIsApiReady] = useState(false);
  const [code, setCode] = useState<string>("");

  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<typeof monaco | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const completionProviderRef = useRef<monaco.IDisposable | null>(null);

  // ✅ Wait for pywebview API
  useEffect(() => {
    const checkApiReady = () => {
      if (window.pywebview?.api) {
        setIsApiReady(true);
        return true;
      }
      return false;
    };

    if (checkApiReady()) return;

    const handleReady = () => checkApiReady();
    window.addEventListener("pywebviewready", handleReady);

    const interval = setInterval(() => checkApiReady(), 100);
    const timeoutId = setTimeout(() => {
      clearInterval(interval);
      console.warn("pywebview API not available in IDEPage");
    }, 5000);

    return () => {
      clearInterval(interval);
      clearTimeout(timeoutId);
      window.removeEventListener("pywebviewready", handleReady);
    };
  }, []);

  // Fetch project + code
  useEffect(() => {
    const fetchProject = async () => {
      if (!isApiReady || !projectId || !window.pywebview?.api) return;
      try {
        const result = await window.pywebview.api.get_project(projectId);
        if (result?.project_id) setProject(result);

        const codeResult = await window.pywebview.api.get_project_code(projectId);
        if (typeof codeResult === "string") setCode(codeResult);
      } catch (err) {
        console.error("❌ Error fetching project/code:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchProject();
  }, [isApiReady, projectId]);

  // ---------- linting ----------
  const lintCode = useCallback(
    async (currentCode: string) => {
      if (!monacoRef.current || !editorRef.current || !isApiReady) return;
      try {
        const board = project?.metadata?.platform || "arduino";
        if (!isApiReady || !projectId || !window.pywebview?.api) return;
        const result = await window.pywebview.api.lint_code(currentCode, board);
        if (!result || !Array.isArray(result.errors)) {
          setErrors([]);
          return;
        }
        const model = editorRef.current.getModel();
        if (!model) return;
        const markers = result.errors.map((err) => ({
          startLineNumber: err.line,
          endLineNumber: err.line,
          startColumn: err.column || 1,
          endColumn: err.column ? err.column + 1 : model.getLineMaxColumn(err.line),
          message: err.message,
          severity: monacoRef.current!.MarkerSeverity.Error,
        }));
        monacoRef.current!.editor.setModelMarkers(model, "python-linter", markers);
        setErrors(result.errors);
      } catch (e) {
        console.error("[ERROR] during lint:", e);
        setErrors([]);
      }
    },
    [project, isApiReady]
  );

  useEffect(() => {
    if (!project || !editorRef.current || !isApiReady) return;
    const timeoutId = setTimeout(() => {
      lintCode(editorRef.current?.getValue() || "");
    }, 500);
    return () => clearTimeout(timeoutId);
  }, [project, lintCode, isApiReady]);

  // ✅ Improved autocomplete provider
  const registerCompletionProvider = useCallback((monacoInstance: typeof monaco) => {
    if (completionProviderRef.current) {
      completionProviderRef.current.dispose();
    }

    completionProviderRef.current = monacoInstance.languages.registerCompletionItemProvider("python", {
      triggerCharacters: [".", "(", "[", '"', "'", " ", ","],
      provideCompletionItems: async (model, position) => {
        try {
          // Check if API is available
          if (!window.pywebview?.api?.get_completions) {
            console.warn("Autocomplete API not available");
            return { suggestions: [] };
          }

          const code = model.getValue();
          const line = position.lineNumber - 1; // Convert to 0-based
          const column = position.column - 1;   // Convert to 0-based

          console.log("Requesting completions at:", { line, column });
          
          const response = await window.pywebview.api.get_completions(code, line, column);
          
          if (!Array.isArray(response)) {
            console.warn("Invalid completion response:", response);
            return { suggestions: [] };
          }

          console.log("Received completions:", response.length);

          const suggestions = response.map((item: CompletionItem) => ({
            label: item.label,
            kind: item.kind || monacoInstance.languages.CompletionItemKind.Function,
            insertText: item.insertText || item.label,
            documentation: item.documentation,
            detail: item.detail,
            range: {
              startLineNumber: position.lineNumber,
              endLineNumber: position.lineNumber,
              startColumn: position.column,
              endColumn: position.column,
            },
          }));

          return { suggestions };

        } catch (err) {
          console.error("[ERROR] Autocomplete request failed:", err);
          return { suggestions: [] };
        }
      },
    });

    console.log("✅ Autocomplete provider registered");
  }, []);

  const handleEditorDidMount = (
    editor: monaco.editor.IStandaloneCodeEditor,
    monacoInstance: typeof monaco
  ) => {
    editorRef.current = editor;
    monacoRef.current = monacoInstance;

    // ✅ Register autocomplete provider
    registerCompletionProvider(monacoInstance);

    let changeTimeout: ReturnType<typeof setTimeout>;
    editor.onDidChangeModelContent(() => {
      clearTimeout(changeTimeout);
      changeTimeout = setTimeout(() => {
        setCode(editor.getValue());
      }, 300);
    });

    // ✅ Enable more completion features
    editor.updateOptions({
      quickSuggestions: { 
        other: true, 
        comments: false, 
        strings: true 
      },
      suggestOnTriggerCharacters: true,
      acceptSuggestionOnEnter: "on",
      tabCompletion: "on",
      wordBasedSuggestions: "allDocuments",
    });
  };

  // Cleanup
  useEffect(() => {
    return () => {
      if (completionProviderRef.current) {
        completionProviderRef.current.dispose();
        completionProviderRef.current = null;
      }
      if (editorRef.current) {
        const model = editorRef.current.getModel();
        if (model) model.dispose();
        editorRef.current.dispose();
        editorRef.current = null;
      }
      monacoRef.current = null;
    };
  }, []);

  // ---------- save ----------
  const handleSaveProject = async () => {
    if (!window.pywebview?.api || !isApiReady || !projectId) return;
    try {
      await window.pywebview.api.save_project_files(projectId, code);
      message.success("Project saved!");
    } catch (err) {
      console.error("❌ Error saving project:", err);
      message.error("Failed to save project");
    }
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
        e.preventDefault();
        handleSaveProject();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [code, projectId, isApiReady]);

  // ---------- compile ----------
  const handleCompile = async () => {
    if (!window.pywebview?.api || !isApiReady || !projectId) return;

    try {
      // 1. Save first
      await window.pywebview.api.save_project_files(projectId, code);
      message.success("Project saved, starting compile...");

      // 2. Call backend compile
      const result = await window.pywebview.api.compile(projectId);
      console.log("Compile result:", result);

      if (result.success) {
        message.success("✅ Compilation successful!");
      } else {
        message.error("❌ Compilation failed: " + (result.error || "Check logs"));
      }
    } catch (err) {
      console.error("❌ Compile error:", err);
      message.error("Compilation failed");
    }
  };

  // UI ----------
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
          <div style={{ height: "calc(100vh - 80px)", display: "flex", flexDirection: "column" }}>
            <ModuleExplorer />
          </div>
        </Sider>

        {/* Main Section */}
        <Layout style={{ background: "#fff" }}>
          <Content style={{ padding: "12px", display: "flex", flexDirection: "column", height: "100vh" }}>
            {/* Header */}
            <Card size="small" style={{ marginBottom: 12 }} bodyStyle={{ padding: "12px" }}>
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
                      {project?.description || "Write your Arduino-compatible Python code below"}
                    </Text>
                  </div>
                  <Space>
                    <Button size="small" icon={<BugOutlined />} onClick={() => lintCode(code)} style={{ borderRadius: 6 }}>
                      Run Lint
                    </Button>
                    <Button size="small" icon={<SaveOutlined />} onClick={handleSaveProject} style={{ borderRadius: 6 }}>
                      Save
                    </Button>
                    <Button size="small" type="primary" icon={<PlayCircleOutlined />} onClick={handleCompile}>
                      <Space size={4}>
                        <UploadOutlined />
                        Compile / Upload
                      </Space>
                    </Button>
                  </Space>
                </div>
              )}
            </Card>

            {/* Editor */}
            <Card
              style={{ flex: 1, display: "flex", flexDirection: "column", padding: 0, overflow: "hidden" }}
              bodyStyle={{ padding: 0, flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}
            >
              <div ref={containerRef} style={{ flex: 1, minHeight: 0, position: "relative", overflow: "hidden" }}>
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
                    renderValidationDecorations: "on",
                    lineNumbersMinChars: 3,
                    folding: false,
                    occurrencesHighlight: "off",
                    selectionHighlight: false,
                    suggestOnTriggerCharacters: true,
                    quickSuggestions: { 
                      other: true, 
                      comments: false, 
                      strings: true 
                    },
                    parameterHints: { enabled: true },
                    wordBasedSuggestions: "allDocuments",
                    acceptSuggestionOnEnter: "on",
                    tabCompletion: "on",
                  }}
                />
              </div>

              {/* Problems panel */}
              {errors.length > 0 && (
                <List
                  size="small"
                  bordered
                  dataSource={errors}
                  style={{ marginTop: 8, maxHeight: 120, overflow: "auto", flexShrink: 0 }}
                  renderItem={(err: any) => (
                    <List.Item
                      onClick={() => {
                        editorRef.current?.revealLineInCenter(err.line);
                        editorRef.current?.setPosition({ lineNumber: err.line, column: err.column || 1 });
                        editorRef.current?.focus();
                      }}
                      style={{ cursor: "pointer", padding: "4px 12px" }}
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