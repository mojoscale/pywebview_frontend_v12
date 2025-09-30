// src/pages/Home.tsx
import React, { useEffect, useState } from "react";
import { List, Button, Typography, Space, Tag, Avatar, Spin } from "antd";
import {
  PlusOutlined,
  DatabaseOutlined,
  SettingOutlined,
  FolderOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";

const { Title, Text } = Typography;

interface Project {
  project_id: string;
  name: string;
  description: string;
  is_active: boolean;
  updated_at: string;
  created_at: string;
  metadata?: Record<string, any>;
}

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        // Direct call to pywebview API
        if (window.pywebview?.api && typeof window.pywebview.api.get_projects === 'function') {
          const result = await window.pywebview.api.get_projects();
          if (Array.isArray(result)) {
            setProjects(result);
          } else {
            console.error("Invalid response from get_projects:", result);
            setProjects([]);
          }
        } else {
          console.error("pywebview API not available");
          setProjects([]);
        }
      } catch (err) {
        console.error("❌ Error fetching projects:", err);
        setProjects([]);
      } finally {
        setLoading(false);
      }
    };

    // Wait for pywebview to be ready
    if (window.pywebview?.api) {
      fetchProjects();
    } else {
      // If not ready, wait for the ready event
      const handleReady = () => {
        fetchProjects();
      };

      window.addEventListener('pywebviewready', handleReady);
      
      // Fallback: try after a short delay
      const timeoutId = setTimeout(() => {
        if (window.pywebview?.api) {
          fetchProjects();
        } else {
          console.error("pywebview API not available after timeout");
          setLoading(false);
        }
      }, 1000);

      return () => {
        window.removeEventListener('pywebviewready', handleReady);
        clearTimeout(timeoutId);
      };
    }
  }, []);

  return (
    <div
      style={{
        padding: "24px",
        width: "100%",
      }}
    >
      {/* Header with actions */}
      <Space
        style={{
          width: "100%",
          justifyContent: "space-between",
          marginBottom: 24,
        }}
      >
        <Title level={2} style={{ margin: 0 }}>
          My Projects
        </Title>
        <Space>
          <Button
            type="default"
            icon={<DatabaseOutlined />}
            onClick={() => navigate("/env_vars")}
          >
            Environment Variables
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate("/create_project")}
          >
            New Project
          </Button>
        </Space>
      </Space>

      {loading ? (
        <Spin fullscreen tip="Loading projects..." />
      ) : projects.length === 0 ? (
        <Text type="secondary">No projects found.</Text>
      ) : (
        <List
          itemLayout="horizontal"
          dataSource={projects}
          renderItem={(project) => (
            <List.Item
              actions={[
                <Button
                  key="open"
                  type="link"
                  icon={<SettingOutlined />}
                  onClick={() => navigate(`/project/${project.project_id}`)}
                >
                  Open
                </Button>,
              ]}
            >
              <List.Item.Meta
                avatar={<Avatar size="large" icon={<FolderOutlined />} />}
                title={
                  <Space>
                    <Text strong>{project.name}</Text>
                    <Tag color={project.is_active ? "green" : "red"}>
                      {project.is_active ? "Active" : "Inactive"}
                    </Tag>
                  </Space>
                }
                description={
                  <>
                    <Text>{project.description}</Text>
                    <br />
                    <Text type="secondary">
                      Last updated: {new Date(project.updated_at).toLocaleString()}
                    </Text>
                  </>
                }
              />
            </List.Item>
          )}
        />
      )}
    </div>
  );
};

export default Home;