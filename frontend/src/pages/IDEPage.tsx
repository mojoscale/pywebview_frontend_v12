// src/pages/IDEPage.tsx
import React, { useState, useEffect } from "react";
import { Layout, Spin } from "antd";
import { useParams } from "react-router-dom";
import ModuleExplorer from "../components/ModuleExplorer";
import IDE from "../components/IDE";

const { Sider, Content } = Layout;

const IDEPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [isApiReady, setIsApiReady] = useState(false);

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

  if (!projectId) {
    return (
      <Layout style={{ minHeight: "100vh", display: "flex", justifyContent: "center", alignItems: "center" }}>
        <Spin size="large" />
      </Layout>
    );
  }

  return (
    <Layout style={{ minHeight: "100vh", overflow: "hidden" }}>
      <Sider width={300} theme="light" style={{ background: '#fafafa' }}>
        <div style={{ padding: "16px", borderBottom: "1px solid #f0f0f0" }}>
          <h5 style={{ margin: 0 }}>Module Explorer</h5>
        </div>
        <div style={{ height: "calc(100vh - 80px)", overflow: 'auto' }}>
          <ModuleExplorer />
        </div>
      </Sider>

      <Layout style={{ background: "#fff" }}>
        <Content style={{ padding: 0 }}>
          <IDE projectId={projectId} isApiReady={isApiReady} />
        </Content>
      </Layout>
    </Layout>
  );
};

export default IDEPage;