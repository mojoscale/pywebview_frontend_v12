// src/pages/CreateProject.tsx
import React, { useState } from "react";
import { Form, Input, Button, Card, Space, Typography, message } from "antd";
import { useNavigate } from "react-router-dom";

const { Title } = Typography;
const { TextArea } = Input;

const CreateProject: React.FC = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (values: any) => {
    const payload = {
      ...values,
    };

    try {
      setLoading(true);
      if (window.pywebview?.api?.create_project) {
        await window.pywebview.api.create_project(payload); // ✅ send dict to backend
        message.success("Project created successfully!");
        navigate("/"); // go back to home after success
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

  return (
    <div style={{ display: "flex", justifyContent: "center", padding: "40px" }}>
      <Card
        style={{ width: "100%", maxWidth: 600, borderRadius: 12, boxShadow: "0 2px 8px rgba(0,0,0,0.05)" }}
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
