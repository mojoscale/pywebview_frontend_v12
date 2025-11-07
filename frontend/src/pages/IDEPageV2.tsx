// src/pages/IDEPageV2.tsx
import React, { useRef, useState, useEffect } from "react";
import { message, Layout, Spin } from "antd";
import LightIDE from "../components/LightIDE";
import type { LightIDERef } from "../components/LightIDE";
import { useParams } from "react-router-dom";

const { Content } = Layout;

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

const IDEPageV2: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const ideRef = useRef<LightIDERef>(null);
  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);
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
      console.warn("pywebview API not available in IDEPageV2");
    }, 5000);

    return () => {
      clearInterval(interval);
      clearTimeout(timeoutId);
      window.removeEventListener("pywebviewready", handleReady);
    };
  }, []);

  // Fetch project details
  useEffect(() => {
    const fetchProjectData = async () => {
      if (!isApiReady || !projectId || !window.pywebview?.api) {
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        
        // Fetch project details
        const projectResult = await window.pywebview.api.get_project(projectId);
        console.log("📦 Fetched project:", projectResult);
        
        if (projectResult?.project_id) {
          setProject(projectResult);
        }

      } catch (err) {
        console.error("❌ Error fetching project data:", err);
        message.error("Failed to load project");
      } finally {
        setIsLoading(false);
      }
    };

    fetchProjectData();
  }, [isApiReady, projectId]);

  // Save method moved to IDEPageV2
  const handleSave = async (): Promise<void> => {
    if (!window.pywebview?.api || !isApiReady || !projectId || !ideRef.current) {
      message.warning("Backend not ready or no project selected");
      return;
    }

    try {
      const currentCode = ideRef.current.getCode();
      await window.pywebview.api.save_project_files(projectId, currentCode);
      message.success("Code saved successfully!");
    } catch (err) {
      console.error("❌ Save error:", err);
      message.error("Failed to save code");
    }
  };

  // Keyboard shortcuts for essential functions
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!ideRef.current) return;

      // Ctrl+S or Cmd+S for Save
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        handleSave();
      }
      // Ctrl+Shift+F or Cmd+Shift+F for Format
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'F') {
        e.preventDefault();
        ideRef.current.formatCode().then(() => {
          message.success("Formatted!");
        });
      }
      // Ctrl+Shift+L or Cmd+Shift+L for Lint
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'L') {
        e.preventDefault();
        ideRef.current.lintCode();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  if (!projectId) {
    return (
      <Layout style={{ 
        height: "100vh", 
        display: "flex", 
        justifyContent: "center", 
        alignItems: "center",
        background: "#1e1e1e"
      }}>
        <Spin size="large" tip="No project selected" />
      </Layout>
    );
  }

  if (isLoading) {
    return (
      <Layout style={{ 
        height: "100vh", 
        display: "flex", 
        justifyContent: "center", 
        alignItems: "center",
        background: "#1e1e1e"
      }}>
        <Spin size="large" tip="Loading project..." />
      </Layout>
    );
  }

  if (!isApiReady) {
    return (
      <Layout style={{ 
        height: "100vh", 
        display: "flex", 
        justifyContent: "center", 
        alignItems: "center",
        background: "#1e1e1e"
      }}>
        <Spin size="large" tip="Initializing backend..." />
      </Layout>
    );
  }

  return (
    <Layout style={{ 
      height: "100vh", 
      overflow: "hidden",
      background: "#1e1e1e"
    }}>
      <Content style={{ 
        padding: 0,
        overflow: "hidden",
        height: "100vh",
        background: "#1e1e1e"
      }}>
        <LightIDE
          ref={ideRef}
          projectId={projectId}
          isApiReady={isApiReady}
          onCodeChange={(code) => {
            console.log("Code changed in project:", project?.name, "Length:", code.length);
          }}
        />
      </Content>
    </Layout>
  );
};

export default IDEPageV2;