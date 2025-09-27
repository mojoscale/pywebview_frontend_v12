// src/App.tsx
import { useEffect, useState } from "react";
import { Routes, Route, useNavigate, useLocation } from "react-router-dom";
import { Layout, Typography, Button, Space, Tag } from "antd";
import { HomeOutlined, PlusOutlined } from "@ant-design/icons";
import UpdateBanner from "./components/UpdateBanner";
import Home from "./pages/Home";
import CreateProject from "./pages/CreateProject";
import IDEPage from "./pages/IDEPage";
import { usePywebviewApi } from "./hooks/usePywebviewApi";

const { Header, Footer, Content } = Layout;
const { Text } = Typography;

function App() {
  const [version, setVersion] = useState<string>("");
  const [serialStatus, setSerialStatus] = useState<{
    available: boolean;
    ip?: string;
  }>({ available: false });

  const navigate = useNavigate();
  const location = useLocation();

  const apiVersion = usePywebviewApi("get_version");
  const apiSerial = usePywebviewApi("serial_port_available");

  // ✅ Fetch version
  useEffect(() => {
    const fetchVersion = async () => {
      if (!apiVersion) return;
      try {
        const v = await apiVersion.get_version();
        setVersion(v);
      } catch (err) {
        console.error("❌ Error fetching version:", err);
      }
    };
    fetchVersion();
  }, [apiVersion]);

  // ✅ Fetch serial status
  useEffect(() => {
    const fetchSerial = async () => {
      if (!apiSerial) return;
      try {
        const result = await apiSerial.serial_port_available();
        setSerialStatus(result);
      } catch (err) {
        console.error("❌ Error checking serial:", err);
        setSerialStatus({ available: false });
      }
    };

    fetchSerial();
    const interval = setInterval(fetchSerial, 5000); // poll every 5s
    return () => clearInterval(interval);
  }, [apiSerial]);

  // Determine which button should be highlighted
  const getButtonType = (path: string) => {
    return location.pathname === path ? "primary" : "default";
  };

  return (
    <Layout
      style={{
        minHeight: "100vh",
        width: "100vw",
        margin: 0,
        padding: 0,
      }}
    >
      {/* Top Navigation Bar */}
      <Header
        style={{
          background: "#fff",
          borderBottom: "1px solid #f0f0f0",
          padding: "0 24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          width: "100%",
          margin: 0,
          boxSizing: "border-box",
        }}
      >
        {/* Left side: Branding + Navigation */}
        <div style={{ display: "flex", alignItems: "center" }}>
          <Text strong style={{ fontSize: "18px", marginRight: "32px" }}>
            PyWebView IDE
          </Text>

          <Space>
            <Button
              type={getButtonType("/")}
              icon={<HomeOutlined />}
              onClick={() => navigate("/")}
            >
              Home
            </Button>
            <Button
              type={getButtonType("/create_project")}
              icon={<PlusOutlined />}
              onClick={() => navigate("/create_project")}
            >
              Create Project
            </Button>
          </Space>
        </div>

        {/* Right side: Serial Status + Version */}
        <Space>
          {serialStatus.available ? (
            <Tag color="green">
              Connected {serialStatus.ip ? `(${serialStatus.ip})` : ""}
            </Tag>
          ) : (
            <Tag color="red">Disconnected</Tag>
          )}
          <Text type="secondary" style={{ fontSize: "0.85rem" }}>
            {version ? `v${version}` : "Loading..."}
          </Text>
        </Space>
      </Header>

      {/* Main content */}
      <Content
        style={{
          flex: 1,
          padding: "24px",
          background: "#f0f2f5",
          width: "100%",
          margin: 0,
          boxSizing: "border-box",
        }}
      >
        <UpdateBanner />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/create_project" element={<CreateProject />} />
          <Route path="/project/:projectId" element={<IDEPage />} />
        </Routes>
      </Content>

      {/* Footer */}
      <Footer
        style={{
          textAlign: "center",
          background: "#fff",
          width: "100%",
          margin: 0,
          boxSizing: "border-box",
        }}
      >
        <Text type="secondary" style={{ fontSize: "0.85rem" }}>
          {version ? `Version ${version}` : "Version unknown"}
        </Text>
      </Footer>
    </Layout>
  );
}

export default App;
