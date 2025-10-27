// src/components/ModalProjectForm.tsx
import React, { useState, useEffect } from "react";
import { Form, Input, Button, Space, Select, Spin, Card, Typography } from "antd";

const { TextArea } = Input;
const { Title } = Typography;

interface ModalProjectFormProps {
  initialValues?: {
    name?: string;
    description?: string;
    board_name_id?: string;
  };
  onSubmit: (values: any) => Promise<void>;
  loading?: boolean;
  submitText?: string;
  onCancel?: () => void;
  title?: string;
  cancelPath?: string;
}

const ModalProjectForm: React.FC<ModalProjectFormProps> = ({
  initialValues = {},
  onSubmit,
  title = "Project Form",
  loading = false,
  submitText = "Update Project",
  onCancel,
  cancelPath,
}) => {
  const [form] = Form.useForm();
  const [boards, setBoards] = useState<string[]>([]);
  const [loadingBoards, setLoadingBoards] = useState(true);

  // Fetch available boards via PyWebView API
  useEffect(() => {
    const fetchBoards = async () => {
      try {
        if (window.pywebview?.api?.get_boards) {
          const result = await window.pywebview.api.get_boards();
          if (Array.isArray(result)) {
            setBoards(result);
          }
        }
      } catch (err) {
        console.error("❌ Error fetching boards:", err);
      } finally {
        setLoadingBoards(false);
      }
    };

    fetchBoards();
  }, []);

  // Set initial values when component mounts
  useEffect(() => {
    if (initialValues) {
      console.log("Setting modal form values:", initialValues);
      form.setFieldsValue(initialValues);
    }
  }, [initialValues, form]);

  const handleFormSubmit = async (values: any) => {
    try {
      await onSubmit(values);
    } catch (err) {
      console.error("Error in form submission:", err);
    }
  };

  return (
    <Card
      bordered
      style={{ width: "100%" }}
      bodyStyle={{ padding: "24px" }}
      title={
        <Title level={4} style={{ margin: 0 }}>
          {title}
        </Title>
      }
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleFormSubmit}
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
            <Select
              placeholder="Select a board"
              showSearch
              optionFilterProp="children"
              filterOption={(input, option) =>
                String(option?.children ?? "")
                  .toLowerCase()
                  .includes(input.toLowerCase())
              }
            >
              {boards.map((board) => (
                <Select.Option key={board} value={board}>
                  {board}
                </Select.Option>
              ))}
            </Select>
          )}
        </Form.Item>

        <Form.Item style={{ marginTop: 24, marginBottom: 0 }}>
          <Space style={{ display: "flex", justifyContent: "flex-end" }}>
            <Button onClick={onCancel ?? (() => cancelPath && (window.location.href = cancelPath))}>Cancel</Button>
            <Button type="primary" htmlType="submit" loading={loading}>
              {submitText}
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default ModalProjectForm;
