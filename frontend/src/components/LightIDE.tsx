// src/components/LightIDE.tsx
import React, { useState, useEffect, useRef, useCallback, forwardRef, useImperativeHandle } from "react";
import { Spin } from "antd";
import MonacoEditor from "@monaco-editor/react";
import type * as monaco from "monaco-editor";

interface LightIDEProps {
  projectId: string;
  isApiReady: boolean;
  initialCode?: string;
  onCodeChange?: (code: string) => void;
}

export interface LightIDERef {
  getCode: () => string;
  setCode: (code: string) => void;
  formatCode: () => Promise<void>;
  lintCode: () => Promise<void>;
  // saveCode removed from here
}

const LightIDE = forwardRef<LightIDERef, LightIDEProps>(({ 
  projectId, 
  isApiReady, 
  initialCode = "",
  onCodeChange 
}, ref) => {
  const [code, setCode] = useState<string>(initialCode);
  const [isLoading, setIsLoading] = useState(true);
  
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<typeof monaco | null>(null);

  // Expose methods to parent component
  useImperativeHandle(ref, () => ({
    getCode: () => code,
    setCode: (newCode: string) => {
      setCode(newCode);
      if (editorRef.current) {
        editorRef.current.setValue(newCode);
      }
    },
    formatCode: handleFormatCode,
    lintCode: handleLintCode,
    // saveCode removed from here
  }));

  // Load initial code
  useEffect(() => {
    const loadCode = async () => {
      if (!isApiReady || !projectId || !window.pywebview?.api) {
        setIsLoading(false);
        return;
      }

      try {
        const codeResult = await window.pywebview.api.get_project_code(projectId);
        if (typeof codeResult === "string") {
          setCode(codeResult);
        }
      } catch (err) {
        console.error("❌ Error loading code:", err);
      } finally {
        setIsLoading(false);
      }
    };

    loadCode();
  }, [isApiReady, projectId]);

  // Handle code changes
  const handleCodeChange = useCallback((newCode: string | undefined) => {
    const currentCode = newCode || "";
    setCode(currentCode);
    onCodeChange?.(currentCode);
  }, [onCodeChange]);

  // Format code
  const handleFormatCode = async (): Promise<void> => {
    if (!window.pywebview?.api || !isApiReady) return;

    try {
      const formattedCode = await window.pywebview.api.format_code(code);
      setCode(formattedCode);
      if (editorRef.current) {
        editorRef.current.setValue(formattedCode);
      }
    } catch (err) {
      console.error("❌ Formatting error:", err);
    }
  };

  // Lint code
  const handleLintCode = async (): Promise<void> => {
    if (!monacoRef.current || !editorRef.current || !isApiReady) return;

    try {
      const result = await window.pywebview.api.lint_code(code, "arduino");
      
      if (!result || !Array.isArray(result.errors)) return;

      const model = editorRef.current.getModel();
      if (!model) return;

      const markers = result.errors.map((err: any) => ({
        startLineNumber: err.line,
        endLineNumber: err.line,
        startColumn: err.column || 1,
        endColumn: err.column ? err.column + 1 : model.getLineMaxColumn(err.line),
        message: err.message,
        severity: monacoRef.current!.MarkerSeverity.Error,
      }));

      monacoRef.current.editor.setModelMarkers(model, "python-linter", markers);
    } catch (err) {
      console.error("❌ Linting error:", err);
    }
  };

  // Handle editor mount
  const handleEditorDidMount = (
    editor: monaco.editor.IStandaloneCodeEditor,
    monacoInstance: typeof monaco
  ) => {
    editorRef.current = editor;
    monacoRef.current = monacoInstance;

    editor.updateOptions({
      quickSuggestions: { other: true, comments: false, strings: true },
      suggestOnTriggerCharacters: true,
      acceptSuggestionOnEnter: "on",
      tabCompletion: "on",
      wordBasedSuggestions: "allDocuments",
      parameterHints: { enabled: true },
      automaticLayout: true,
      minimap: { enabled: true },
      scrollBeyondLastLine: false,
      smoothScrolling: true,
      cursorSmoothCaretAnimation: "on",
      fontSize: 14,
      lineHeight: 1.5,
    });
  };

  // Auto-lint on code changes
  useEffect(() => {
    if (!code || !isApiReady) return;

    const timeoutId = setTimeout(() => {
      handleLintCode();
    }, 1000);

    return () => clearTimeout(timeoutId);
  }, [code, isApiReady]);

  if (!isApiReady || isLoading) {
    return (
      <div style={{ 
        display: "flex", 
        justifyContent: "center", 
        alignItems: "center", 
        height: "100%",
        background: "#1e1e1e" 
      }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <MonacoEditor
      language="python"
      value={code}
      theme="vs-dark"
      onMount={handleEditorDidMount}
      onChange={handleCodeChange}
      options={{
        fontSize: 14,
        lineHeight: 1.5,
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
        padding: { top: 0, bottom: 0 },
        smoothScrolling: true,
        mouseWheelScrollSensitivity: 1.2,
        cursorSmoothCaretAnimation: 'on',
      }}
      loading={
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100%',
          background: '#1e1e1e',
        }}>
          <Spin size="large" />
        </div>
      }
    />
  );
});

export default LightIDE;