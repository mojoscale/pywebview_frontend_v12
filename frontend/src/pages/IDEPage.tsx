import React, { useState, useEffect, useRef } from "react";
import { Layout, Spin, Button, Modal } from "antd";
import { useParams } from "react-router-dom";
import ModuleExplorer from "../components/ModuleExplorer";
import IDE from "../components/IDE";
import { MenuFoldOutlined, MenuUnfoldOutlined } from "@ant-design/icons";

const { Sider, Content, Header } = Layout;

const IDEPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [isApiReady, setIsApiReady] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [modalMessages, setModalMessages] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isSiderCollapsed, setIsSiderCollapsed] = useState(false);
  const logEndRef = useRef<HTMLDivElement | null>(null);

  // Scroll modal to bottom as messages stream in
  useEffect(() => {
    if (logEndRef.current) logEndRef.current.scrollIntoView({ behavior: "smooth" });
  }, [modalMessages]);

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

  // Real-time messages from backend
  useEffect(() => {
    window.__updateBuildStatus = (phase: string, message: string) => {
      setModalMessages(prev => [...prev, `${phase.toUpperCase()}: ${message}`]);
    };
  }, []);

  // Trigger backend compile call
  const handleCompile = async (withUpload = false) => {
    if (!isApiReady || !window.pywebview?.api) {
      Modal.warning({
        title: "Backend not ready",
        content: "Please wait for PyWebView API to initialize.",
      });
      return;
    }

    setModalMessages([]);
    setIsModalVisible(true);
    setIsUploading(withUpload);

    try {
      const res = await window.pywebview.api.compile(projectId, withUpload);
      if (res.success) {
        setModalMessages(prev => [...prev, "✅ Build completed successfully"]);
      } else {
        setModalMessages(prev => [
          ...prev,
          `❌ Build failed: ${res.error || res.message}`,
        ]);
      }
    } catch (err: any) {
      console.error(err);
      setModalMessages(prev => [
        ...prev,
        `❌ Error: ${err.message || err.toString()}`,
      ]);
    }
  };

  const toggleSider = () => {
    setIsSiderCollapsed(!isSiderCollapsed);
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
    <Layout style={{ minHeight: "100vh", overflow: "hidden" }}>
      {/* Collapsible Sidebar */}
      <Sider 
        width={300} 
        theme="light" 
        style={{ background: "#fafafa" }}
        collapsed={isSiderCollapsed}
        collapsedWidth={0}
        trigger={null}
        collapsible
      >
        <div style={{ padding: "16px", borderBottom: "1px solid #f0f0f0" }}>
          <h5 style={{ margin: 0 }}>Module Explorer</h5>
        </div>
        <div style={{ height: "calc(100vh - 80px)", overflow: "auto" }}>
          <ModuleExplorer />
        </div>
      </Sider>

      {/* Main content with buttons */}
      <Layout style={{ background: "#fff" }}>
        <Header
          style={{
            background: "#fff",
            borderBottom: "1px solid #f0f0f0",
            padding: "8px 16px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "8px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            {/* Toggle button for module explorer */}
            <Button 
              type="text"
              icon={isSiderCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={toggleSider}
              title={isSiderCollapsed ? "Show Module Explorer" : "Hide Module Explorer"}
              style={{ 
                border: "1px solid #d9d9d9",
                display: "flex",
                alignItems: "center",
                justifyContent: "center"
              }}
            />
            
            {/* Compile buttons */}
            <Button type="primary" onClick={() => handleCompile(false)}>
              Compile
            </Button>
            <Button type="primary" danger onClick={() => handleCompile(true)}>
              Compile & Upload
            </Button>
          </div>
        </Header>

        <Content style={{ padding: 0 }}>
          <IDE projectId={projectId} isApiReady={isApiReady} />
        </Content>
      </Layout>

      {/* Modal showing compile progress */}
      <Modal
        open={isModalVisible}
        title={isUploading ? "Compiling & Uploading..." : "Compiling..."}
        onCancel={() => setIsModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setIsModalVisible(false)}>
            Close
          </Button>,
        ]}
        width={600}
      >
        <div
          style={{
            background: "#111",
            color: "#0f0",
            fontFamily: "monospace",
            padding: "12px",
            height: "50vh",
            overflowY: "auto",
            borderRadius: "6px",
          }}
        >
          {modalMessages.length === 0 ? (
            <div>⏳ Starting build process...</div>
          ) : (
            modalMessages.map((msg, i) => <div key={i}>{msg}</div>)
          )}
          <div ref={logEndRef} />
        </div>
      </Modal>
    </Layout>
  );
};

export default IDEPage;