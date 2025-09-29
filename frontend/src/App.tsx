import { useEffect, useState } from "react";
import { Routes, Route, useNavigate, useLocation } from "react-router-dom";
import { Layout, Typography, Button, Space, Tag } from "antd";
import { HomeOutlined, PlusOutlined, CodeOutlined, CloseOutlined } from "@ant-design/icons";
import UpdateBanner from "./components/UpdateBanner";
import Home from "./pages/Home";
import CreateProject from "./pages/CreateProject";
import IDEPage from "./pages/IDEPage";
import EnvironmentVariablesForm from "./pages/EnvironmentVariablesForm";
import { usePywebviewApi } from "./hooks/usePywebviewApi";
import TerminalView from "./components/TerminalView";

const { Header, Footer, Content } = Layout;
const { Text } = Typography;

function App() {
  const [version, setVersion] = useState<string>("");
  const [serialStatus, setSerialStatus] = useState<{ available: boolean; ip?: string }>({
    available: false,
  });
  const [showTerminal, setShowTerminal] = useState(false);
  const [terminalHeight, setTerminalHeight] = useState(300);

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
    const interval = setInterval(fetchSerial, 5000);
    return () => clearInterval(interval);
  }, [apiSerial]);

  const getButtonType = (path: string) => {
    return location.pathname === path ? "primary" : "default";
  };

  return (
    <Layout style={{ 
      minHeight: "100vh", 
      width: "100vw",
      position: "relative",
      paddingBottom: showTerminal ? `${terminalHeight}px` : "0px",
      transition: "padding-bottom 0.3s ease-in-out"
    }}>
      {/* Top Navigation Bar */}
      <Header
        style={{
          background: "#fff",
          borderBottom: "1px solid #f0f0f0",
          padding: "0 24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          position: "sticky",
          top: 0,
          zIndex: 100,
          height: "64px",
          flexShrink: 0,
        }}
      >
        {/* Left side */}
        <div style={{ display: "flex", alignItems: "center" }}>
          <Text strong style={{ fontSize: "18px", marginRight: "32px" }}>
            mojoscale
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

        {/* Right side */}
        <Space>
          <Button
            type={showTerminal ? "primary" : "default"}
            icon={showTerminal ? <CloseOutlined /> : <CodeOutlined />}
            onClick={() => setShowTerminal((prev) => !prev)}
          >
            {showTerminal ? "Hide Terminal" : "Show Terminal"}
          </Button>

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
      <Content style={{ 
        flex: 1, 
        padding: "24px", 
        background: "#f0f2f5",
        overflow: "auto",
        minHeight: "calc(100vh - 128px)", // Account for header and footer
      }}>
        <UpdateBanner />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/create_project" element={<CreateProject />} />
          <Route path="/project/:projectId" element={<IDEPage />} />
          <Route path="/env_vars" element={<EnvironmentVariablesForm />} />
        </Routes>
      </Content>

      {/* Footer */}
      <Footer style={{ 
        textAlign: "center", 
        background: "#fff",
        borderTop: "1px solid #f0f0f0",
        padding: "16px 24px",
        height: "64px",
        flexShrink: 0,
      }}>
        <Text type="secondary" style={{ fontSize: "0.85rem" }}>
          {version ? `Version ${version}` : "Version unknown"}
        </Text>
      </Footer>

      {/* Terminal - Fixed at bottom */}
      {showTerminal && (
        <div style={{
          position: "fixed",
          bottom: 0,
          left: 0,
          right: 0,
          zIndex: 1000,
          height: `${terminalHeight}px`,
          transition: "height 0.3s ease-in-out",
        }}>
          <TerminalView 
            onClose={() => setShowTerminal(false)}
            onHeightChange={setTerminalHeight}
          />
        </div>
      )}
    </Layout>
  );
}

export default App;