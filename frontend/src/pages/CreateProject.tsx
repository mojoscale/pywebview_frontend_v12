// src/pages/CreateProject.tsx
import React, { useState } from "react";
import { message } from "antd";
import { useNavigate } from "react-router-dom";
import ProjectForm from "../components/ProjectForm";

const CreateProject: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (values: any) => {
    const payload = {
      ...values,
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

  return (
    <ProjectForm
      onSubmit={handleSubmit}
      loading={loading}
      submitText="Create Project"
      title="Create New Project"
      showCancel={true}
      cancelPath="/"
    />
  );
};

export default CreateProject;