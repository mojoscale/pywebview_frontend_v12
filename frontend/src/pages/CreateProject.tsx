// src/pages/CreateProject.tsx
import React, { useState, useEffect } from "react";
import { Form, Input, Button, Card, Space, Typography, message, Select, Spin } from "antd";
import { useNavigate } from "react-router-dom";

const { Title } = Typography;
const { TextArea } = Input;

const CreateProject: React.FC = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [boards, setBoards] = useState<string[]>([]);
  const [loadingBoards, setLoadingBoards] = useState(true);
  const [isApiReady, setIsApiReady] = useState(false);

  // ✅ Wait for pywebview API to be ready
  useEffect(() => {
    const checkApiReady = () => {
      if (window.pywebview?.api) {
        setIsApiReady(true);
        return true;
      }
      return false;
    };

    if (checkApiReady()) {
      return;
    }

    const handleReady = () => {
      if (checkApiReady()) {
        console.log("pywebview API ready in CreateProject");
      }
    };

    window.addEventListener("pywebviewready", handleReady);

    const interval = setInterval(() => {
      if (checkApiReady()) {
        clearInterval(interval);
      }
    }, 100);

    const timeoutId = setTimeout(() => {
      clearInterval(interval);
      console.warn("pywebview API not available in CreateProject");
    }, 5000);

    return () => {
      clearInterval(interval);
      clearTimeout(timeoutId);
      window.removeEventListener("pywebviewready", handleReady);
    };
  }, []);

  // ✅ Fetch boards when API is ready
  useEffect(() => {
    const fetchBoards = async () => {
      if (!isApiReady || !window.pywebview?.api) return;

      try {
        const result = await window.pywebview.api.get_boards();
        if (Array.isArray(result)) {
          setBoards(result);
        } else {
          console.error("Invalid response from get_boards:", result);
          setBoards([]);
        }
      } catch (err) {
        console.error("❌ Error fetching boards:", err);
        setBoards([]);
      } finally {
        setLoadingBoards(false);
      }
    };

    fetchBoards();
  }, [isApiReady]);

  const handleSubmit = async (values: any) => {
    const payload = {
      ...values, // will include board_name_id now
    };

    try {
      setLoading(true);
      if (window.pywebview?.api?.create_project) {
        await window.pywebview.api.create_project(payload);
        message.success("Project created successfully!");
        navigate("/");
      } else {
        message.error("❌ Backend API not available");
      }
    } catch (err) {
      console.error("Error creating project:", err);
      message.error("Failed to create project.");
    } finally {
      setLoading(false);
    }
  };

  // Show loading while waiting for API
  if (!isApiReady) {
    return (
      <div style={{ display: "flex", justifyContent: "center", padding: "40px" }}>
        <Card style={{ width: "100%", maxWidth: 600, textAlign: "center" }}>
          <Spin size="large" tip="Initializing..." />
        </Card>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", justifyContent: "center", padding: "40px" }}>
      <Card
        style={{
          width: "100%",
          maxWidth: 600,
          borderRadius: 12,
          boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
        }}
      >
        <Title level={3} style={{ textAlign: "center", marginBottom: 24 }}>
          Create New Project
        </Title>

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          autoComplete="off"
        >
          <Form.Item
            name="name"
            label="Project Name"
            rules={[{ required: true, message: "Please enter a project name" }]}
          >
            <Input placeholder="Enter project name" />
          </Form.Item>

          <Form.Item name="description" label="Description">
            <TextArea rows={3} placeholder="Brief description of the project" />
          </Form.Item>

          <Form.Item
            name="board_name_id"
            label="Board"
            rules={[{ required: true, message: "Please select a board" }]}
          >
            {loadingBoards ? (
              <Spin size="small" />
            ) : (
              <Select placeholder="Select a board">
                {boards.map((board) => (
                  <Select.Option key={board} value={board}>
                    {board}
                  </Select.Option>
                ))}
              </Select>
            )}
          </Form.Item>

          <Form.Item style={{ marginTop: 24 }}>
            <Space style={{ display: "flex", justifyContent: "flex-end" }}>
              <Button onClick={() => navigate("/")}>Cancel</Button>
              <Button type="primary" htmlType="submit" loading={loading}>
                Create Project
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default CreateProject;
