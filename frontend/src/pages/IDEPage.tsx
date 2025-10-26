// src/pages/IDEPage.tsx
import React, { useState, useEffect, useRef, useCallback } from "react";
import { 
  Layout, 
  Typography, 
  Card, 
  Button, 
  Space, 
  Spin, 
  List, 
  message,
  Modal,
  FloatButton,
  Tag
} from "antd";
import {
  PlayCircleOutlined,
  CodeOutlined,
  FileSearchOutlined,
  UploadOutlined,
  BugOutlined,
  SaveOutlined,
  EyeOutlined,
  EyeInvisibleOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined
} from "@ant-design/icons";
import MonacoEditor from "@monaco-editor/react";
import type * as monaco from "monaco-editor";
import ModuleExplorer from "../components/ModuleExplorer";
import ArduinoTranspilerLog from "../components/ArduinoTranspilerLog";
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
  kind: number | string;
  insertText?: string;
  documentation?: string;
  detail?: string;
}

interface CompilationResult {
  success: boolean;
  message?: string;
  error?: string;
  fileName?: string;
  warnings?: string[];
  suggestions?: string[];
  specs?: {
    flash: { used: number; total: number };
    ram: { used: number; total: number };
    additional?: { [key: string]: string };
  };
  timestamp?: string;
}

const IDEPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState<any[]>([]);
  const [isApiReady, setIsApiReady] = useState(false);
  const [code, setCode] = useState<string>("");
  const [isCompiling, setIsCompiling] = useState(false);
  const [compilationResult, setCompilationResult] = useState<CompilationResult | null>(null);
  const [showCompilationResult, setShowCompilationResult] = useState(false);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);
  const [isResultMinimized, setIsResultMinimized] = useState(false);

  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<typeof monaco | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const completionProviderRef = useRef<monaco.IDisposable | null>(null);
  
  // Completion caching and request deduplication
  const completionCacheRef = useRef<Map<string, CompletionItem[]>>(new Map());
  const pendingRequestRef = useRef<Promise<CompletionItem[]> | null>(null);
  const lastRequestKeyRef = useRef<string>("");
  const COMPLETION_CACHE_SIZE = 50;

  // Wait for pywebview API
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

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

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

  // Poll for compilation results
  const startPollingForResults = useCallback(async () => {
    if (!projectId || !window.pywebview?.api) return;

    const poll = async () => {
      try {
        const status = await window.pywebview.api.get_compile_status(projectId);
        
        if (status && status.completed) {
          // Stop polling
          if (pollingInterval) {
            clearInterval(pollingInterval);
            setPollingInterval(null);
          }
          
          setIsCompiling(false);
          
          // Format the result
          const formattedResult: CompilationResult = {
            success: status.success,
            fileName: project?.name || "sketch.ino",
            message: status.message,
            error: status.error,
            warnings: status.warnings || [],
            suggestions: status.suggestions || [],
            specs: status.specs,
            timestamp: new Date().toISOString(),
          };

          setCompilationResult(formattedResult);
          setShowCompilationResult(true);
          setIsResultMinimized(false); // Show the result when it first arrives

          if (status.success) {
            message.success("✅ Compilation successful!");
          } else {
            message.error("❌ Compilation failed");
          }
        }
      } catch (err) {
        console.error("❌ Error polling compilation status:", err);
      }
    };

    // Start polling every 2 seconds
    const interval = setInterval(poll, 2000);
    setPollingInterval(interval);

    // Initial poll
    poll();
  }, [projectId, project, pollingInterval]);

  // Linting
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
    [project, isApiReady, projectId]
  );

  useEffect(() => {
    if (!project || !editorRef.current || !isApiReady) return;
    const timeoutId = setTimeout(() => {
      lintCode(editorRef.current?.getValue() || "");
    }, 500);
    return () => clearTimeout(timeoutId);
  }, [project, lintCode, isApiReady]);

  // Helper function to map kind strings to Monaco kind enums
  const getMonacoKind = (monacoInstance: typeof monaco, kind?: number | string): number => {
    if (typeof kind === "number") {
      return kind;
    }

    const kindMap: Record<string, number> = {
      function: monacoInstance.languages.CompletionItemKind.Function,
      class: monacoInstance.languages.CompletionItemKind.Class,
      variable: monacoInstance.languages.CompletionItemKind.Variable,
      module: monacoInstance.languages.CompletionItemKind.Module,
      keyword: monacoInstance.languages.CompletionItemKind.Keyword,
      method: monacoInstance.languages.CompletionItemKind.Method,
      property: monacoInstance.languages.CompletionItemKind.Property,
      enum: monacoInstance.languages.CompletionItemKind.Enum,
      interface: monacoInstance.languages.CompletionItemKind.Interface,
      text: monacoInstance.languages.CompletionItemKind.Text,
    };

    return kindMap[String(kind).toLowerCase()] || monacoInstance.languages.CompletionItemKind.Text;
  };

  // Completion provider setup (unchanged from your original)
  const getCompletionsWithCache = useCallback(
    async (code: string, line: number, column: number): Promise<CompletionItem[]> => {
      // ... (keep your existing completion logic)
      return [];
    },
    [isApiReady, projectId]
  );

  const registerCompletionProvider = useCallback(
    (monacoInstance: typeof monaco) => {
      // ... (keep your existing completion provider logic)
    },
    [getCompletionsWithCache]
  );

  const handleEditorDidMount = (
    editor: monaco.editor.IStandaloneCodeEditor,
    monacoInstance: typeof monaco
  ) => {
    editorRef.current = editor;
    monacoRef.current = monacoInstance;

    registerCompletionProvider(monacoInstance);

    let changeTimeout: ReturnType<typeof setTimeout>;
    editor.onDidChangeModelContent(() => {
      clearTimeout(changeTimeout);
      changeTimeout = setTimeout(() => {
        setCode(editor.getValue());
      }, 300);
    });

    editor.updateOptions({
      quickSuggestions: { other: true, comments: false, strings: true },
      suggestOnTriggerCharacters: true,
      acceptSuggestionOnEnter: "on",
      tabCompletion: "on",
      wordBasedSuggestions: "allDocuments",
      parameterHints: { enabled: true },
    });

    console.log('✅ Editor mounted and completion provider ready');
  };

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
      completionCacheRef.current.clear();
      pendingRequestRef.current = null;
    };
  }, []);

  // Save project
  const handleSaveProject = async () => {
    if (!window.pywebview?.api || !isApiReady || !projectId) return;
    try {
      await window.pywebview.api.save_project_files(projectId, code);
      message.success("Project saved!");
      await lintCode(code);
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

  // Compile function
  const handleCompile = async () => {
    if (!window.pywebview?.api || !isApiReady || !projectId) return;

    setIsCompiling(true);
    setCompilationResult(null);
    setShowCompilationResult(false);
    setIsResultMinimized(false);

    try {
      // Save first
      await window.pywebview.api.save_project_files(projectId, code);
      message.success("Project saved, starting compile...");

      // Schedule compilation (this returns immediately)
      const result = await window.pywebview.api.compile(projectId);
      
      if (result.success) {
        message.info("🔄 Compilation scheduled...");
        // Start polling for results
        startPollingForResults();
      } else {
        setIsCompiling(false);
        message.error(`❌ Failed to schedule compilation: ${result.error}`);
      }

    } catch (err) {
      console.error("❌ Compile error:", err);
      setIsCompiling(false);
      const errorResult: CompilationResult = {
        success: false,
        fileName: project?.name || "sketch.ino",
        error: err instanceof Error ? err.message : "Unknown error occurred",
        timestamp: new Date().toISOString()
      };
      setCompilationResult(errorResult);
      setShowCompilationResult(true);
      setIsResultMinimized(false);
      message.error("Failed to start compilation");
    }
  };

  const handleRetryCompile = () => {
    setShowCompilationResult(false);
    setIsResultMinimized(false);
    setCompilationResult(null);
    
    // Stop any existing polling
    if (pollingInterval) {
      clearInterval(pollingInterval);
      setPollingInterval(null);
    }
    
    handleCompile();
  };

  const handleDownloadHex = () => {
    message.info("Downloading HEX file...");
    // Implement: window.pywebview.api.download_hex(projectId);
  };

  const handleCloseResult = () => {
    setShowCompilationResult(false);
    setIsResultMinimized(true); // Minimize instead of completely hiding
    
    // Stop polling when user manually closes
    if (pollingInterval) {
      clearInterval(pollingInterval);
      setPollingInterval(null);
    }
  };

  const handleToggleResult = () => {
    if (isResultMinimized) {
      setShowCompilationResult(true);
      setIsResultMinimized(false);
    } else {
      setShowCompilationResult(false);
      setIsResultMinimized(true);
    }
  };

  const handleHideResult = () => {
    setShowCompilationResult(false);
    setIsResultMinimized(false);
    setCompilationResult(null);
    
    // Stop polling
    if (pollingInterval) {
      clearInterval(pollingInterval);
      setPollingInterval(null);
    }
  };

  if (!isApiReady) {
    return (
      <Layout
        style={{
          minHeight: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <Spin size="large" />
      </Layout>
    );
  }

  return (
    <Layout style={{ minHeight: "100vh", overflow: "hidden" }}>
      {/* Compilation Modal */}
      <Modal
        open={isCompiling}
        footer={null}
        closable={false}
        width={400}
        style={{ textAlign: 'center' }}
      >
        <Space direction="vertical" size="large" style={{ width: '100%', padding: '20px 0' }}>
          <Spin size="large" />
          <Title level={4} style={{ margin: 0 }}>Compiling...</Title>
          <Text type="secondary">Please wait while your code is being compiled</Text>
          <Text type="secondary" style={{ fontSize: 12 }}>
            This may take a few moments
          </Text>
        </Space>
      </Modal>

      <Layout>
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

        <Layout style={{ background: "#fff" }}>
          <Content
            style={{
              padding: "12px",
              display: "flex",
              flexDirection: "column",
              height: "100vh",
            }}
          >
            <Card 
              size="small" 
              style={{ marginBottom: 12 }}
              styles={{ body: { padding: "12px" } }}
            >
              {loading ? (
                <Spin size="small" />
              ) : (
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: "12px",
                    alignItems: "flex-start",
                  }}
                >
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
                    <Button
                      size="small"
                      icon={<BugOutlined />}
                      onClick={() => lintCode(code)}
                      style={{ borderRadius: 6 }}
                      disabled={isCompiling}
                    >
                      Run Lint
                    </Button>
                    <Button
                      size="small"
                      icon={<SaveOutlined />}
                      onClick={handleSaveProject}
                      style={{ borderRadius: 6 }}
                      disabled={isCompiling}
                    >
                      Save
                    </Button>
                    <Button
                      size="small"
                      type="primary"
                      icon={<PlayCircleOutlined />}
                      onClick={handleCompile}
                      loading={isCompiling}
                      disabled={isCompiling}
                    >
                      <Space size={4}>
                        <UploadOutlined />
                        Compile / Upload
                      </Space>
                    </Button>
                  </Space>
                </div>
              )}
            </Card>

            {/* Compilation Result - Full View */}
            {showCompilationResult && compilationResult && (
              <ArduinoTranspilerLog
                compilationResult={compilationResult}
                onRetry={handleRetryCompile}
                onDownload={handleDownloadHex}
                onClose={handleCloseResult}
              />
            )}

            {/* Minimized Result Bar */}
            {isResultMinimized && compilationResult && (
              <Card 
                size="small" 
                style={{ 
                  marginBottom: 12,
                  border: compilationResult.success ? '1px solid #52c41a' : '1px solid #ff4d4f',
                  background: compilationResult.success ? '#f6ffed' : '#fff2f0'
                }}
                styles={{ body: { padding: '8px 12px' } }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Space>
                    {compilationResult.success ? (
                      <CheckCircleOutlined style={{ color: '#52c41a' }} />
                    ) : (
                      <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
                    )}
                    <Text strong>
                      {compilationResult.success ? 'Compilation Successful' : 'Compilation Failed'}
                    </Text>
                    {compilationResult.fileName && (
                      <Tag icon={<FileTextOutlined />} color="blue" size="small">
                        {compilationResult.fileName}
                      </Tag>
                    )}
                    {compilationResult.error && (
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {compilationResult.error.length > 100 
                          ? compilationResult.error.substring(0, 100) + '...' 
                          : compilationResult.error}
                      </Text>
                    )}
                  </Space>
                  <Space>
                    <Button 
                      size="small" 
                      icon={<EyeOutlined />}
                      onClick={handleToggleResult}
                    >
                      Show Details
                    </Button>
                    <Button 
                      size="small" 
                      type="text" 
                      icon={<EyeInvisibleOutlined />}
                      onClick={handleHideResult}
                    >
                      Dismiss
                    </Button>
                  </Space>
                </div>
              </Card>
            )}

            <Card
              style={{
                flex: 1,
                display: "flex",
                flexDirection: "column",
                padding: 0,
                overflow: "hidden",
                opacity: isCompiling ? 0.6 : 1,
                pointerEvents: isCompiling ? 'none' : 'auto'
              }}
              styles={{
                body: {
                  padding: 0,
                  flex: 1,
                  display: "flex",
                  flexDirection: "column",
                  overflow: "hidden",
                }
              }}
            >
              <div
                ref={containerRef}
                style={{
                  flex: 1,
                  minHeight: 0,
                  position: "relative",
                  overflow: "hidden",
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
                    renderValidationDecorations: "on",
                    lineNumbersMinChars: 3,
                    folding: false,
                    occurrencesHighlight: "off",
                    selectionHighlight: false,
                    suggestOnTriggerCharacters: true,
                    quickSuggestions: { other: true, comments: false, strings: true },
                    parameterHints: { enabled: true },
                    wordBasedSuggestions: "allDocuments",
                    acceptSuggestionOnEnter: "on",
                    tabCompletion: "on",
                    readOnly: isCompiling,
                  }}
                />
              </div>

              {errors.length > 0 && (
                <List
                  size="small"
                  bordered
                  dataSource={errors}
                  style={{
                    marginTop: 8,
                    maxHeight: 120,
                    overflow: "auto",
                    flexShrink: 0,
                  }}
                  renderItem={(err: any) => (
                    <List.Item
                      onClick={() => {
                        if (isCompiling) return;
                        editorRef.current?.revealLineInCenter(err.line);
                        editorRef.current?.setPosition({
                          lineNumber: err.line,
                          column: err.column || 1,
                        });
                        editorRef.current?.focus();
                      }}
                      style={{ 
                        cursor: isCompiling ? 'not-allowed' : 'pointer', 
                        padding: "4px 12px",
                        opacity: isCompiling ? 0.6 : 1
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

            {/* Floating button to show minimized results */}
            {isResultMinimized && compilationResult && (
              <FloatButton
                icon={compilationResult.success ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
                type={compilationResult.success ? "default" : "primary"}
                style={{ 
                  right: 24,
                  bottom: 24,
                  backgroundColor: compilationResult.success ? '#52c41a' : '#ff4d4f'
                }}
                onClick={handleToggleResult}
                tooltip={compilationResult.success ? "Show compilation results" : "Show compilation errors"}
              />
            )}
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
};

export default IDEPage;