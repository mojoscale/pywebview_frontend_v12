import React, { useState, useEffect, useRef } from "react";
import { Layout, Spin, Button, Modal, Progress, Alert, Steps, notification } from "antd";
import { useParams } from "react-router-dom";
import ModuleExplorer from "../components/ModuleExplorer";
import IDE from "../components/IDE";
import { 
    MenuFoldOutlined, 
    MenuUnfoldOutlined, 
    CodeOutlined,
    BuildOutlined,
    UploadOutlined,
    CheckCircleOutlined
} from "@ant-design/icons";

import type { Project, Board, EnvVariable, CompileStatus, CompletionItem } from '../types';

// Extend Window interface to include our custom properties
declare global {
    interface Window {
        __onCompilerEvent?: (ev: any) => void;
        __appendTerminalLog?: (logLine: string) => void;
        pywebview?: {
            api?: {
                // Compilation methods
                compile: (projectId: string, withUpload?: boolean) => Promise<any>;
                cancel_session?: (sessionId: string) => Promise<void>;
                get_compile_status: (projectId: string) => Promise<CompileStatus>;
                
                // Project methods
                get_projects: () => Promise<Project[]>;
                get_project: (projectId: string) => Promise<Project>;
                get_project_code: (projectId: string) => Promise<{code: string}>;
                create_project: (payload: any) => Promise<any>;
                update_project: (payload: any) => Promise<any>;
                save_project_files: (projectId: string, code: string) => Promise<void>;
                
                // Board methods
                get_boards: () => Promise<Board[]>;
                
                // Code analysis methods
                lint_code: (code: string, board: string) => Promise<{errors: Array<{
                    line: number;
                    column: number;
                    message: string;
                    severity: string;
                }>}>;
                format_code: (code: string) => Promise<string>;
                get_completions: (code: string, line: number, column: number) => Promise<CompletionItem[]>;
                
                // Environment variables methods
                get_all_env: () => Promise<EnvVariable[]>;
                update_env_value: (key: string, value: string, isSecret?: boolean) => Promise<void>;
                create_env_value: (key: string, value: string, isSecret?: boolean) => Promise<void>;
                delete_env_value: (key: string) => Promise<void>;
                bulk_create_env: (pairs: Array<{key: string; value: string}>) => Promise<void>;
                
                // Serial communication methods
                start_serial_monitor: () => Promise<any>;
                stop_serial_monitor: () => Promise<any>;
                send_serial_command: (command: string) => Promise<any>;
                serial_port_available: () => Promise<boolean>;
                
                // System methods
                get_version: () => Promise<string>;
            };
        };
    }
}

// Define Status type for Steps component
type Status = 'wait' | 'process' | 'finish' | 'error';

const { Sider, Content, Header } = Layout;
const { Step } = Steps;

const IDEPage: React.FC = () => {
    const { projectId } = useParams<{ projectId: string }>();
    const [isApiReady, setIsApiReady] = useState(false);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [isSiderCollapsed, setIsSiderCollapsed] = useState(false);
    const [currentPhase, setCurrentPhase] = useState<string>("");
    const [progressPercent, setProgressPercent] = useState<number>(0);
    const [finalResult, setFinalResult] = useState<any>(null);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [showUploadPrompt, setShowUploadPrompt] = useState(false);
    const [hasCompilationError, setHasCompilationError] = useState(false);
    const [hasUploadError, setHasUploadError] = useState(false);
    const [uploadLogs, setUploadLogs] = useState<string[]>([]);
    const [showUploadLogs, setShowUploadLogs] = useState(false);
    const logEndRef = useRef<HTMLDivElement | null>(null);

    // Phase → progress mapping
    const phaseProgress: Record<string, number> = {
        begin_transpile: 10,
        end_transpile: 25,
        begin_compile: 40,
        end_compile: 70,
        start_upload: 80,
        end_upload: 95,
        all_done: 100,
        error: 100,
        cancelled: 100,
    };

    // Auto-scroll upload logs
    useEffect(() => {
        if (logEndRef.current && showUploadLogs) {
            logEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [uploadLogs, showUploadLogs]);

    // PyWebView API readiness
    useEffect(() => {
        const checkApi = () => {
            if (window.pywebview?.api) {
                setIsApiReady(true);
                return true;
            }
            return false;
        };
        if (checkApi()) return;
        const interval = setInterval(() => checkApi(), 100);
        return () => clearInterval(interval);
    }, []);

    // Unified backend event handler
    useEffect(() => {
        const handleCompilerEvent = (ev: any) => {
            const { phase, text } = ev;
            console.log(`[EVENT] ${phase}: ${text}`);
            
            setCurrentPhase(phase);
            setProgressPercent(phaseProgress[phase] ?? progressPercent);

            // Track errors
            if (phase === "error") {
                if (text.includes("Compilation failed") || text.includes("Build failed")) {
                    setHasCompilationError(true);
                    setShowUploadPrompt(false);
                } else if (text.includes("Upload failed") || text.includes("No compatible device")) {
                    setHasUploadError(true);
                }
            }

            // Show upload prompt when compilation completes successfully
            if (phase === "end_compile" && isUploading && !hasCompilationError) {
                setShowUploadPrompt(true);
                setShowUploadLogs(true); // Start showing logs when upload phase begins
            }

            // Capture upload logs - look for progress indicators
            if (showUploadLogs && text) {
                const lowerText = text.toLowerCase();
                // Capture important upload-related messages
                if (lowerText.includes('upload') || 
                    lowerText.includes('writing') || 
                    lowerText.includes('flash') ||
                    lowerText.includes('boot') ||
                    lowerText.includes('serial') ||
                    lowerText.includes('progress') ||
                    lowerText.includes('%') ||
                    lowerText.includes('bytes') ||
                    lowerText.includes('hash') ||
                    lowerText.includes('leaving') ||
                    text.includes('❌') ||
                    text.includes('✅') ||
                    text.includes('⚠️')) {
                    setUploadLogs(prev => [...prev, text]);
                }
            }

            // Handle completion
            if (phase === "all_done" || phase === "error" || phase === "cancelled") {
                const success = determineOverallSuccess(phase, hasCompilationError, hasUploadError, isUploading);
                const result = {
                    success,
                    error: !success ? getFinalErrorMessage(hasCompilationError, hasUploadError, text) : undefined,
                    phase: phase
                };
                setFinalResult(result);
                setShowUploadPrompt(false);
            }
        };

        // Also capture terminal logs during upload phase
        const handleTerminalLog = (logLine: string) => {
            if (showUploadLogs && logLine && logLine.trim()) {
                const lowerLine = logLine.toLowerCase();
                // Capture upload progress indicators
                if (lowerLine.includes('writing at') || 
                    lowerLine.includes('uploading') ||
                    lowerLine.includes('%') ||
                    lowerLine.includes('bytes') ||
                    lowerLine.includes('compressed') ||
                    lowerLine.includes('hash of data verified') ||
                    lowerLine.includes('leaving...') ||
                    lowerLine.includes('hard resetting')) {
                    setUploadLogs(prev => [...prev, logLine]);
                }
            }
        };

        // Assign handlers to window
        window.__onCompilerEvent = handleCompilerEvent;
        window.__appendTerminalLog = handleTerminalLog;

        return () => {
            window.__onCompilerEvent = undefined;
            window.__appendTerminalLog = undefined;
        };
    }, [progressPercent, isUploading, hasCompilationError, hasUploadError, showUploadLogs, phaseProgress, sessionId]);

    // Determine overall success based on all phases
    const determineOverallSuccess = (finalPhase: string, compilationError: boolean, uploadError: boolean, wasUploading: boolean) => {
        if (finalPhase === "error" || finalPhase === "cancelled") {
            return false;
        }
        if (compilationError) {
            return false;
        }
        if (wasUploading && uploadError) {
            return false;
        }
        return finalPhase === "all_done";
    };

    // Get appropriate error message
    const getFinalErrorMessage = (compilationError: boolean, uploadError: boolean, lastErrorText: string) => {
        if (compilationError) {
            return "Compilation failed - check your code for errors";
        }
        if (uploadError) {
            return "Upload failed - check device connection";
        }
        return lastErrorText || "Build process failed";
    };

    // Reset modal when closed
    useEffect(() => {
        if (!isModalVisible) {
            setProgressPercent(0);
            setFinalResult(null);
            setCurrentPhase("");
            setSessionId(null);
            setShowUploadPrompt(false);
            setHasCompilationError(false);
            setHasUploadError(false);
            setUploadLogs([]);
            setShowUploadLogs(false);
        }
    }, [isModalVisible]);

    // Start compile - SIMPLIFIED: Always start new compilation
    const handleCompile = async (withUpload = false) => {
        if (!isApiReady || !window.pywebview?.api) {
            Modal.warning({
                title: "Backend not ready",
                content: "PyWebView API not initialized.",
            });
            return;
        }

        if (!projectId) {
            Modal.warning({
                title: "Project ID missing",
                content: "Unable to determine project ID.",
            });
            return;
        }

        // Start new compilation
        startNewCompilation(withUpload);
    };

    const startNewCompilation = async (withUpload: boolean) => {
        setIsModalVisible(true);
        setIsUploading(withUpload);
        setProgressPercent(0);
        setCurrentPhase("begin_transpile");
        setFinalResult(null);
        setShowUploadPrompt(false);
        setHasCompilationError(false);
        setHasUploadError(false);
        setUploadLogs([]);
        setShowUploadLogs(false);

        try {
            // Safe access to window.pywebview.api
            if (window.pywebview?.api?.compile) {
                const res = await window.pywebview.api.compile(projectId!, withUpload);
                setSessionId(res.session_id || null);
            } else {
                throw new Error("Compile API not available");
            }
        } catch (err: any) {
            setCurrentPhase("error");
            setProgressPercent(100);
            setHasCompilationError(true);
        }
    };

    const toggleSider = () => setIsSiderCollapsed(!isSiderCollapsed);

    // Status color
    const getStatusColor = () => {
        if (currentPhase === "error" || hasCompilationError || hasUploadError) return "#ff4d4f";
        if (currentPhase === "cancelled") return "#faad14";
        if (currentPhase === "all_done" && !hasCompilationError && (!isUploading || !hasUploadError)) return "#52c41a";
        return "#1890ff";
    };

    const getStatusText = () => {
        if (hasCompilationError) return "Compilation failed";
        if (hasUploadError) return "Upload failed";
        
        if (showUploadPrompt) {
            return "Ready for upload - follow instructions below";
        }
        
        switch (currentPhase) {
            case "begin_transpile": return "Preparing code...";
            case "end_transpile": return "Code preparation complete";
            case "begin_compile": return "Compiling firmware...";
            case "end_compile": return "Compilation successful";
            case "start_upload": return "Uploading to device...";
            case "end_upload": return "Upload complete!";
            case "all_done": return "All steps completed successfully";
            case "cancelled": return "Cancelled by user";
            case "error": return "Error occurred";
            default: return "Processing...";
        }
    };

    // Get current step for the Steps component
    const getCurrentStep = () => {
        if (["error", "cancelled"].includes(currentPhase) || hasCompilationError || hasUploadError) return -1;
        if (currentPhase === "all_done") return isUploading ? 3 : 2;
        if (currentPhase.includes("upload") || showUploadPrompt) return 2;
        if (currentPhase.includes("compile")) return 1;
        return 0;
    };

    // Get phase status
    const getPhaseStatus = (phase: string): Status => {
        if (currentPhase === "error" || hasCompilationError || hasUploadError) {
            if (phase === "transpile" && hasCompilationError) return "error";
            if (phase === "compile" && hasCompilationError) return "error";
            if (phase === "upload" && hasUploadError) return "error";
            return "wait";
        }
        
        if (currentPhase === "cancelled") return "wait";
        
        if (phase === "transpile") {
            if (currentPhase.includes("transpile")) return "process";
            if (currentPhase.includes("compile") || currentPhase.includes("upload") || showUploadPrompt) return "finish";
            return "wait";
        }
        
        if (phase === "compile") {
            if (currentPhase.includes("compile")) return "process";
            if (currentPhase.includes("upload") || showUploadPrompt) return "finish";
            return "wait";
        }
        
        if (phase === "upload") {
            if (currentPhase.includes("upload") || showUploadPrompt) return "process";
            if (currentPhase === "all_done") return "finish";
            return "wait";
        }
        
        return "wait";
    };

    // Format upload log messages with colors
    const formatLogMessage = (msg: string) => {
        const lower = msg.toLowerCase();
        if (lower.includes("error") || lower.includes("failed") || msg.includes("❌") || lower.includes("fatal"))
            return <span style={{ color: "#ff4d4f" }}>{msg}</span>;
        if (lower.includes("warning") || msg.includes("⚠️"))
            return <span style={{ color: "#faad14" }}>{msg}</span>;
        if (lower.includes("success") || msg.includes("✅") || lower.includes("hash of data verified") || lower.includes("leaving..."))
            return <span style={{ color: "#52c41a" }}>{msg}</span>;
        if (lower.includes("upload") || lower.includes("writing") || lower.includes("bytes") || lower.includes("%"))
            return <span style={{ color: "#1890ff" }}>{msg}</span>;
        return <span style={{ color: "#ccc" }}>{msg}</span>;
    };

    if (!projectId) {
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
        <Layout style={{ minHeight: "100vh" }}>
            <Sider
                width={300}
                theme="light"
                style={{ background: "#fafafa" }}
                collapsed={isSiderCollapsed}
                collapsedWidth={0}
                trigger={null}
                collapsible
            >
                <div style={{ padding: 16, borderBottom: "1px solid #f0f0f0" }}>
                    <h5 style={{ margin: 0 }}>Module Explorer</h5>
                </div>
                <div style={{ height: "calc(100vh - 80px)", overflow: "auto" }}>
                    <ModuleExplorer />
                </div>
            </Sider>

            <Layout style={{ background: "#fff" }}>
                <Header
                    style={{
                        background: "#fff",
                        borderBottom: "1px solid #f0f0f0",
                        padding: "8px 16px",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                    }}
                >
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <Button
                            type="text"
                            icon={isSiderCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                            onClick={toggleSider}
                        />
                        <Button 
                            type="primary" 
                            icon={<BuildOutlined />}
                            onClick={() => handleCompile(false)}
                        >
                            Compile
                        </Button>
                        <Button 
                            type="primary" 
                            danger 
                            icon={<UploadOutlined />}
                            onClick={() => handleCompile(true)}
                        >
                            Compile & Upload
                        </Button>
                    </div>
                </Header>

                <Content>
                    <IDE projectId={projectId} isApiReady={isApiReady} />
                </Content>
            </Layout>

            {/* Build Modal */}
            <Modal
                open={isModalVisible}
                title={
                    <div>
                        <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
                            {isUploading ? "Compiling & Uploading to Device" : "Compiling Project"}
                        </div>
                        <div style={{ color: getStatusColor(), marginTop: 4, fontSize: '14px' }}>
                            {getStatusText()}
                        </div>
                    </div>
                }
                onCancel={() => setIsModalVisible(false)}
                footer={[
                    <Button 
                        key="close" 
                        type="primary" 
                        onClick={() => setIsModalVisible(false)}
                    >
                        Close
                    </Button>,
                ]}
                width={600}
                style={{ top: 20 }}
            >
                {/* Progress Steps */}
                <Steps
                    current={getCurrentStep()}
                    status={
                        hasCompilationError || hasUploadError ? "error" : 
                        currentPhase === "cancelled" ? "error" : "process"
                    }
                    style={{ marginBottom: 24 }}
                >
                    <Step 
                        title="Preparing code" 
                        description="Getting code ready for compilation"
                        icon={<CodeOutlined />}
                        status={getPhaseStatus("transpile")}
                    />
                    <Step 
                        title="Compiling" 
                        description="Building firmware"
                        icon={<BuildOutlined />}
                        status={getPhaseStatus("compile")}
                    />
                    {isUploading && (
                        <Step 
                            title="Uploading" 
                            description="Flashing to device"
                            icon={<UploadOutlined />}
                            status={getPhaseStatus("upload")}
                        />
                    )}
                    <Step 
                        title="Complete" 
                        description="All done"
                        icon={<CheckCircleOutlined />}
                    />
                </Steps>

                <Progress
                    percent={progressPercent}
                    strokeColor={getStatusColor()}
                    showInfo={true}
                    style={{ marginBottom: 16 }}
                />

                {/* Upload Instructions - Always show during upload phase */}
                {showUploadPrompt && (
                    <Alert
                        message="Upload Instructions"
                        description={
                            <div>
                                <p><strong>For ESP32:</strong> Hold the BOOT button, then the upload will start automatically.</p>
                                <p><strong>Watch the logs below for progress:</strong></p>
                                <ul style={{ fontSize: '12px', color: '#666', margin: '8px 0', paddingLeft: '16px' }}>
                                    <li>When you see "Writing at..." or progress percentage, you can release BOOT button</li>
                                    <li>When you see "Hash of data verified" or "Leaving...", upload is complete</li>
                                </ul>
                            </div>
                        }
                        type="warning"
                        showIcon
                        style={{ marginBottom: 16 }}
                    />
                )}

                {/* Upload Progress Logs - Only show during upload phase */}
                {showUploadLogs && (
                    <div style={{ marginBottom: 16 }}>
                        <div style={{ 
                            fontSize: '14px', 
                            fontWeight: 'bold', 
                            marginBottom: '8px',
                            color: '#1890ff'
                        }}>
                            📤 Upload Progress
                        </div>
                        <div
                            style={{
                                background: "#111",
                                color: "#fff",
                                padding: "12px",
                                borderRadius: "6px",
                                maxHeight: "200px",
                                overflowY: "auto",
                                fontFamily: "'Courier New', monospace",
                                fontSize: "12px",
                                lineHeight: "1.4",
                            }}
                        >
                            {uploadLogs.length === 0 ? (
                                <div style={{ color: "#777" }}>
                                    Waiting for upload to start... Hold BOOT button if required.
                                </div>
                            ) : (
                                uploadLogs.map((log, i) => (
                                    <div key={i} style={{ marginBottom: "2px" }}>
                                        {formatLogMessage(log)}
                                    </div>
                                ))
                            )}
                            <div ref={logEndRef} />
                        </div>
                    </div>
                )}

                {/* Final summary */}
                {finalResult && (
                    <Alert
                        message={finalResult.success ? "✅ Build Successful" : "❌ Build Failed"}
                        description={
                            finalResult.success 
                                ? "All operations completed successfully" 
                                : finalResult.error || "Build process encountered an error"
                        }
                        type={finalResult.success ? "success" : "error"}
                        showIcon
                        style={{ marginBottom: 16 }}
                    />
                )}

                {/* Current Status Message - Only show when no other specific content */}
                {!finalResult && !showUploadPrompt && !showUploadLogs && (
                    <div style={{ 
                        textAlign: 'center', 
                        padding: '20px', 
                        color: '#666',
                        fontStyle: 'italic'
                    }}>
                        {getStatusText()}
                    </div>
                )}
            </Modal>
        </Layout>
    );
};

export default IDEPage;