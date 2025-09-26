// src/App.tsx
import { useEffect, useState } from "react";
import { Routes, Route } from "react-router-dom";
import { Layout, Typography } from "antd";
import UpdateBanner from "./components/UpdateBanner";
import Home from "./pages/Home";
import CreateProject from "./pages/CreateProject";
import IDEPage from "./pages/IDEPage";
import { usePywebviewApi } from "./hooks/usePywebviewApi";

const { Header, Footer, Content } = Layout;
const { Text } = Typography;

function App() {
  const [version, setVersion] = useState<string>("");
  const api = usePywebviewApi("get_version");

  useEffect(() => {
    const fetchVersion = async () => {
      if (!api) return;
      try {
        const v = await api.get_version();
        setVersion(v);
      } catch (err) {
        console.error("❌ Error fetching version:", err);
      }
    };
    fetchVersion();
  }, [api]);

  return (
    <Layout style={{ 
      minHeight: "100vh", 
      width: "100vw", // Ensure full viewport width
      margin: 0, // Remove any default margins
      padding: 0 // Remove any default padding
    }}>
      {/* Top bar */}
      <Header
        style={{
          background: "#001529",
          padding: "0 24px",
          display: "flex",
          alignItems: "center",
          color: "#fff",
          fontSize: "1.1rem",
          fontWeight: 500,
          width: "100%", // Ensure full width
          margin: 0,
          boxSizing: "border-box" // Include padding in width calculation
        }}
      >
        Mojoscale IDE
      </Header>

      {/* Main content */}
      <Content
        style={{
          flex: 1,
          padding: "24px",
          background: "#f0f2f5",
          width: "100%", // Ensure full width
          margin: 0,
          boxSizing: "border-box" // Include padding in width calculation
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
      <Footer style={{ 
        textAlign: "center", 
        background: "#fff",
        width: "100%", // Ensure full width
        margin: 0,
        boxSizing: "border-box"
      }}>
        <Text type="secondary" style={{ fontSize: "0.85rem" }}>
          {version ? `Version ${version}` : "Version unknown"}
        </Text>
      </Footer>
    </Layout>
  );
}

export default App;