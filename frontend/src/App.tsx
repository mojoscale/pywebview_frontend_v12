import { useEffect, useState } from "react";
import { Routes, Route, useNavigate, useLocation } from "react-router-dom";
import { Layout, Typography, Button, Space, Tag } from "antd";
import { HomeOutlined, PlusOutlined, CodeOutlined } from "@ant-design/icons";
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
    <>
      {/* Main App Layout */}
      <Layout style={{ 
        minHeight: "100vh", 
        width: "100vw",
        paddingBottom: showTerminal ? "40vh" : "0px", // Add padding when terminal is open
        transition: "padding-bottom 0.2s ease-in-out" // Smooth transition
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
          }}
        >
          {/* Left side */}
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

          {/* Right side */}
          <Space>
            <Button
              type={showTerminal ? "primary" : "default"}
              icon={<CodeOutlined />}
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
          // Remove any bottom padding here since we're handling it at Layout level
        }}>
          <UpdateBanner />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/create_project" element={<CreateProject />} />
            <Route path="/project/:projectId" element={<IDEPage />} />
            <Route path="/env_vars" element={ <EnvironmentVariablesForm /> } />
          </Routes>
        </Content>

        {/* Footer */}
        <Footer style={{ textAlign: "center", background: "#fff" }}>
          <Text type="secondary" style={{ fontSize: "0.85rem" }}>
            {version ? `Version ${version}` : "Version unknown"}
          </Text>
        </Footer>
      </Layout>

      {/* Terminal - Rendered outside the main layout */}
      {showTerminal && (
        <div style={{
          position: "fixed",
          bottom: 0,
          left: 0,
          right: 0,
          zIndex: 1000,
          height: "40vh",
          backgroundColor: "#1e1e1e",
          boxShadow: "0 -2px 10px rgba(0,0,0,0.3)" // Optional: add shadow for better visual separation
        }}>
          <TerminalView onClose={() => setShowTerminal(false)} />
        </div>
      )}
    </>
  );
}

export default App;