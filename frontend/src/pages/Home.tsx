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
import { usePywebviewApi } from "../hooks/usePywebviewApi";

const { Title, Text } = Typography;

interface Project {
  id: string;
  name: string;
  description: string;
  lastUpdated: string;
  status: string;
}

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const api = usePywebviewApi("get_projects");

  useEffect(() => {
    const fetchProjects = async () => {
      if (!api) return;
      try {
        const result = await api.get_projects();
        if (Array.isArray(result)) {
          setProjects(result);
        } else {
          console.error("Invalid response from get_projects:", result);
          setProjects([]);
        }
      } catch (err) {
        console.error("❌ Error fetching projects:", err);
        setProjects([]);
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, [api]);

  return (
    <div
      style={{
        padding: "24px",
        width: "100%", // ✅ expand to full parent width
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
            onClick={() => navigate("/env")}
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
                  onClick={() => navigate(`/project/${project.id}`)}
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
                    <Tag color={project.status === "Active" ? "green" : "red"}>
                      {project.status}
                    </Tag>
                  </Space>
                }
                description={
                  <>
                    <Text>{project.description}</Text>
                    <br />
                    <Text type="secondary">
                      Last updated: {project.lastUpdated}
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
