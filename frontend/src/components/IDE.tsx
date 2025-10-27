// src/components/IDE.tsx
import React, { useState, useEffect, useRef, useCallback } from "react";
import { 
  Card, 
  Button, 
  Space, 
  Spin, 
  List, 
  message,
  Modal,
  FloatButton,
  Tag,
  Form,
  Input,
  Select,
  Typography
} from "antd";
import {
  PlayCircleOutlined,
  CodeOutlined,
  UploadOutlined,
  BugOutlined,
  SaveOutlined,
  EyeOutlined,
  EyeInvisibleOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SettingOutlined
} from "@ant-design/icons";
import MonacoEditor from "@monaco-editor/react";
import type * as monaco from "monaco-editor";
import ArduinoTranspilerLog from "./ArduinoTranspilerLog";

const { Title, Text } = Typography;
const { TextArea } = Input;

interface Project {
  project_id: string;
  name: string;
  description: string;
  is_active: boolean;
  updated_at: string;
  created_at: string;
  project_type: string;
  metadata?: {
    platform?: string;
    board_name?: string;
    board_id?: string;
    board_name_id?: string;
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

interface IDEProps {
  projectId: string;
  isApiReady: boolean;
}

// BoardSelect Component
const BoardSelect: React.FC<{ value?: string; onChange?: (value: string) => void }> = ({ value, onChange }) => {
  const [boards, setBoards] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBoards = async () => {
      try {
        if (window.pywebview?.api?.get_boards) {
          const result = await window.pywebview.api.get_boards();
          console.log("Fetched boards:", result);
          if (Array.isArray(result)) {
            setBoards(result);
          }
        }
      } catch (err) {
        console.error("❌ Error fetching boards:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchBoards();
  }, []);

  return (
    <Select 
      placeholder="Select a board" 
      showSearch 
      optionFilterProp="children"
      loading={loading}
      value={value}
      onChange={onChange}
      filterOption={(input, option) =>
        String(option?.children ?? '').toLowerCase().includes(input.toLowerCase())
      }
    >
      {boards.map((board) => (
        <Select.Option key={board} value={board}>
          {board}
        </Select.Option>
      ))}
    </Select>
  );
};

const IDE: React.FC<IDEProps> = ({ projectId, isApiReady }) => {
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState<any[]>([]);
  const [code, setCode] = useState<string>("");
  const [isCompiling, setIsCompiling] = useState(false);
  const [compilationResult, setCompilationResult] = useState<CompilationResult | null>(null);
  const [showCompilationResult, setShowCompilationResult] = useState(false);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);
  const [isResultMinimized, setIsResultMinimized] = useState(false);
  const [showProjectSettings, setShowProjectSettings] = useState(false);
  const [updatingProject, setUpdatingProject] = useState(false);
  
  // Board info from metadata
  const [boardInfo, setBoardInfo] = useState({
    board_name: "",
    board_id: "",
    platform: "",
    board_name_id: ""
  });
  
  const [form] = Form.useForm();

  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<typeof monaco | null>(null);
  const completionProviderRef = useRef<monaco.IDisposable | null>(null);
  
  // Completion caching and request deduplication
  const completionCacheRef = useRef<Map<string, CompletionItem[]>>(new Map());
  const pendingRequestRef = useRef<Promise<CompletionItem[]> | null>(null);
  const lastRequestKeyRef = useRef<string>("");
  const COMPLETION_CACHE_SIZE = 50;

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  // Fetch project + code and extract board info from metadata
  const fetchProject = useCallback(async () => {
    if (!isApiReady || !projectId || !window.pywebview?.api) return;
    try {
      const result = await window.pywebview.api.get_project(projectId);
      console.log("📦 Fetched project:", result);
      
      if (result?.project_id) {
        setProject(result);
        
        // Extract board info from metadata
        const metadata = result.metadata || {};
        const boardInfo = {
          board_name: metadata.board_name || "",
          board_id: metadata.board_id || "",
          platform: metadata.platform || "",
          board_name_id: metadata.board_name_id || ""
        };
        
        setBoardInfo(boardInfo);
        console.log("🎯 Extracted board info:", boardInfo);
      }

      const codeResult = await window.pywebview.api.get_project_code(projectId);
      if (typeof codeResult === "string") setCode(codeResult);
    } catch (err) {
      console.error("❌ Error fetching project/code:", err);
    } finally {
      setLoading(false);
    }
  }, [isApiReady, projectId]);

  // Add this effect to handle error display
  useEffect(() => {
    if (errors.length > 0 && editorRef.current) {
      // If there are errors, ensure the first error is visible
      const firstError = errors[0];
      if (firstError && firstError.line === 1) {
        // Small delay to ensure editor is fully rendered
        setTimeout(() => {
          editorRef.current?.revealLineInCenter(1);
          editorRef.current?.setPosition({
            lineNumber: firstError.line,
            column: firstError.column || 1,
          });
        }, 100);
      }
    }
  }, [errors]);


  useEffect(() => {
    fetchProject();
  }, [fetchProject]);

  // Poll for compilation results
  const startPollingForResults = useCallback(async () => {
    if (!projectId || !window.pywebview?.api) return;

    const poll = async () => {
      try {
        const status = await window.pywebview?.api?.get_compile_status(projectId);
        
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
          setIsResultMinimized(false);

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
        const board = boardInfo.platform || "arduino";
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
    [boardInfo, isApiReady, projectId]
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

  // Completion provider setup - ACTUALLY IMPLEMENTED
  const getCompletionsWithCache = useCallback(
    async (code: string, line: number, column: number): Promise<CompletionItem[]> => {
      const requestKey = `${line}:${column}:${code.substring(Math.max(0, column - 20), column)}`;
      
      // Check cache first
      if (completionCacheRef.current.has(requestKey)) {
        return completionCacheRef.current.get(requestKey)!;
      }

      // Deduplicate simultaneous requests
      if (pendingRequestRef.current && lastRequestKeyRef.current === requestKey) {
        return pendingRequestRef.current;
      }

      try {
        if (!isApiReady || !projectId || !window.pywebview?.api?.get_completions) {
          return [];
        }

        pendingRequestRef.current = window.pywebview.api.get_completions(code, line, column);
        lastRequestKeyRef.current = requestKey;

        const completions = await pendingRequestRef.current;
        
        // Cache the result
        if (completionCacheRef.current.size >= COMPLETION_CACHE_SIZE) {
          const firstKey = completionCacheRef.current.keys().next().value;
          if (firstKey){
            completionCacheRef.current.delete(firstKey);

          }
          
        }
        completionCacheRef.current.set(requestKey, completions);

        return completions;
      } catch (error) {
        console.error("Error fetching completions:", error);
        return [];
      } finally {
        pendingRequestRef.current = null;
      }
    },
    [isApiReady, projectId]
  );

  const registerCompletionProvider = useCallback(
    (monacoInstance: typeof monaco) => {
      if (completionProviderRef.current) {
        completionProviderRef.current.dispose();
      }

      const provider = monacoInstance.languages.registerCompletionItemProvider('python', {
        triggerCharacters: ['.', '('],
        provideCompletionItems: async (model, position) => {
          const code = model.getValue();
          const line = position.lineNumber;
          const column = position.column;

          try {
            const completions = await getCompletionsWithCache(code, line, column);
            
            const suggestions = completions.map(completion => ({
              label: completion.label,
              kind: getMonacoKind(monacoInstance, completion.kind),
              documentation: completion.documentation,
              detail: completion.detail,
              insertText: completion.insertText || completion.label,
              range: {
                startLineNumber: line,
                endLineNumber: line,
                startColumn: column,
                endColumn: column
              }
            }));

            return { suggestions };
          } catch (error) {
            console.error('Error in completion provider:', error);
            return { suggestions: [] };
          }
        }
      });

      completionProviderRef.current = provider;
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
  // Remove prettier imports and update handleSaveProject:

  // Save project with formatting
  const handleSaveProject = async () => {
    if (!window.pywebview?.api || !isApiReady || !projectId) return;
    try {
      let formattedCode = code;
      
      // Try to format code using backend
      try {
        if (window.pywebview?.api?.format_code) {
          formattedCode = await window.pywebview.api.format_code(code);
          
          // Update the editor with formatted code
          setCode(formattedCode);
          if (editorRef.current) {
            editorRef.current.setValue(formattedCode);
          }
          
          console.log("✅ Code formatted successfully");
        }
      } catch (formatError) {
        console.warn("⚠️ Code formatting failed, saving without format:", formatError);
        // Continue with original code if formatting fails
      }
      
      // Save the (possibly formatted) code
      await window.pywebview.api.save_project_files(projectId, formattedCode);
      message.success("Project saved and formatted!");
      
      // Lint the code after saving
      await lintCode(formattedCode);
      
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
    setIsResultMinimized(true);
    
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

  // Project settings handlers
  const handleOpenProjectSettings = () => {
    setShowProjectSettings(true);
    // Reset form with current values when opening
    if (project) {
      const formValues = {
        name: project.name,
        description: project.description,
        board_name_id: boardInfo.board_name_id || ""
      };
      console.log("📝 Setting form values:", formValues);
      form.setFieldsValue(formValues);
    }
  };

  const handleCloseProjectSettings = () => {
    setShowProjectSettings(false);
  };

  const handleUpdateProject = async (values: any) => {
    if (!projectId) return;

    console.log("🚀 FORM SUBMITTED VALUES:", values);
    console.log("🎯 SELECTED BOARD:", values.board_name_id);

    const payload = {
      ...values,
      project_id: projectId,
    };

    try {
      setUpdatingProject(true);
      if (window.pywebview?.api?.update_project) {
        await window.pywebview.api.update_project(payload);
        message.success("Project updated successfully!");
        // Refresh project data to get updated board info
        await fetchProject();
        handleCloseProjectSettings();
      } else {
        message.error("❌ Backend API not available");
      }
    } catch (err) {
      console.error("Error updating project:", err);
      message.error("Failed to update project.");
    } finally {
      setUpdatingProject(false);
    }
  };

  if (!isApiReady) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", overflow: 'hidden' }}>
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

      {/* Project Settings Modal */}
      <Modal
        open={showProjectSettings}
        onCancel={handleCloseProjectSettings}
        footer={null}
        width={600}
        title="Project Settings"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleUpdateProject}
          autoComplete="off"
        >
          <Form.Item name="name" label="Project Name">
            <Input placeholder="Enter project name" />
          </Form.Item>

          <Form.Item name="description" label="Description">
            <TextArea rows={3} placeholder="Brief description of the project" />
          </Form.Item>

          <Form.Item name="board_name_id" label="Board">
            <BoardSelect 
              onChange={(value) => {
                console.log("🎯 User selected board:", value);
                form.setFieldsValue({ board_name_id: value });
              }}
            />
          </Form.Item>

          <Form.Item style={{ marginTop: 24, marginBottom: 0 }}>
            <Space style={{ display: "flex", justifyContent: "flex-end" }}>
              <Button onClick={handleCloseProjectSettings}>
                Cancel
              </Button>
              <Button 
                type="primary" 
                htmlType="submit" 
                loading={updatingProject}
              >
                Update Project
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Project Header Card */}
      <Card 
        size="small" 
        style={{ 
          marginBottom: 16,
          borderRadius: 8
        }}
        bodyStyle={{ 
          padding: "16px",
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start'
        }}
      >
        {loading ? (
          <Spin size="small" />
        ) : (
          <>
            <div style={{ flex: 1 }}>
              <Space direction="vertical" size={8} style={{ width: '100%' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <CodeOutlined style={{ color: "#1890ff", fontSize: '18px' }} />
                  <Title level={4} style={{ margin: 0, color: '#1890ff' }}>
                    {project ? project.name : "Unknown Project"}
                  </Title>
                  <Button
                    type="text"
                    icon={<SettingOutlined />}
                    size="small"
                    onClick={handleOpenProjectSettings}
                    title="Project Settings"
                  />
                </div>
                
                {project?.description && (
                  <Text type="secondary" style={{ fontSize: "14px", display: 'block' }}>
                    {project.description}
                  </Text>
                )}
                
                {/* Display current board info - NO GREEN HIGHLIGHT */}
                <div>
                  <Text style={{ fontSize: "12px" }}>
                    <strong>Board:</strong> {boardInfo.board_name_id || boardInfo.board_name || "No board selected"}
                  </Text>
                  {(boardInfo.board_id || boardInfo.platform) && (
                    <Text type="secondary" style={{ fontSize: "11px", display: 'block', marginTop: 2 }}>
                      {boardInfo.board_id && `ID: ${boardInfo.board_id}`}
                      {boardInfo.board_id && boardInfo.platform && ' • '}
                      {boardInfo.platform && `Platform: ${boardInfo.platform}`}
                    </Text>
                  )}
                </div>
              </Space>
            </div>
            
            <Space>
              <Button
                size="middle"
                icon={<BugOutlined />}
                onClick={() => lintCode(code)}
                disabled={isCompiling}
              >
                Run Lint
              </Button>
              <Button
                size="middle"
                icon={<SaveOutlined />}
                onClick={handleSaveProject}
                disabled={isCompiling}
              >
                Save
              </Button>
              <Button
                size="middle"
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
          </>
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
                <Tag icon={<FileTextOutlined />} color="blue" >
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

      {/* Editor Card */}
      <Card
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          padding: 0,
          overflow: "hidden",
          borderRadius: 8,
          opacity: isCompiling ? 0.6 : 1,
          pointerEvents: isCompiling ? 'none' : 'auto'
        }}
        bodyStyle={{
          padding: 0,
          flex: 1,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        <div style={{
          flex: 1,
          minHeight: 0,
          position: "relative",
          overflow: "hidden",
        }}>
          <MonacoEditor
            language="python"
            value={code}
            theme="vs-dark"
            onMount={handleEditorDidMount}
            onChange={(val) => setCode(val || "")}
            options={{
              fontSize: 14,
              minimap: { enabled: true },
              scrollBeyondLastLine: false,
              automaticLayout: true,
              wordWrap: 'on',
              lineNumbers: 'on',
              glyphMargin: true,
              folding: true,
              lineDecorationsWidth: 10,
              lineNumbersMinChars: 3,
              renderLineHighlight: 'all',
              readOnly: isCompiling,
              padding: {
                top: 5,
              },
              hover: {
                enabled: true,
                sticky: false,
                above: false,
              },
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
    </div>
  );
};

export default IDE;