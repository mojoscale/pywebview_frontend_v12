import { useState, useEffect } from 'react';
import {
  Form,
  Input,
  Button,
  Card,
  Table,
  Space,
  Tag,
  Modal,
  message,
  Typography,
  Divider,
  Popconfirm,
  Tooltip,
  Switch,
  Alert
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  EditOutlined,
  EyeOutlined,
  EyeInvisibleOutlined,
  CopyOutlined,
  CloudServerOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;
const { TextArea } = Input;

const EnvironmentVariablesForm = () => {
  const [form] = Form.useForm();
  const [variables, setVariables] = useState<any[]>([]);
  const [editingKey, setEditingKey] = useState<string | null>(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [bulkEditVisible, setBulkEditVisible] = useState(false);
  const [bulkText, setBulkText] = useState('');
  const [showSecrets, setShowSecrets] = useState(false);
  const [currentIsSecret, setCurrentIsSecret] = useState(false); // New state for tracking

  // -----------------------------
  // Backend integration helpers
  // -----------------------------
  const fetchVars = async () => {
    try {
      if (!window.pywebview?.api) return;
      const result = await window.pywebview.api.get_all_env();
      const parsed = Object.entries(result).map(([key, data]: [string, any]) => ({
        key,
        value: data.value,
        isSecret: data.is_secret,
      }));
      setVariables(parsed);
    } catch (err) {
      console.error(err);
      message.error('Failed to load environment variables');
    }
  };

  const handleAdd = async () => {
    try {
      const values = await form.validateFields();
      const existingIndex = variables.findIndex(v => v.key === values.key);

      if (existingIndex > -1 && editingKey !== values.key) {
        message.error('Environment variable with this key already exists');
        return;
      }

      // Use the currentIsSecret state instead of form value
      const isSecret = currentIsSecret;
      
      console.log('Form values:', values);
      console.log('isSecret value:', isSecret, 'Type:', typeof isSecret);

      if (editingKey) {
        // Update existing variable
        if (!window.pywebview?.api) return;
        await window.pywebview.api.update_env_value(
          values.key,
          values.value,
          isSecret
        );
        message.success('Variable updated successfully');
        setEditingKey(null);
      } else {
        // Create new variable
        if (!window.pywebview?.api) return;
        await window.pywebview.api.create_env_value(
          values.key,
          values.value,
          isSecret
        );
        message.success('Variable added successfully');
      }

      form.resetFields();
      setCurrentIsSecret(false); // Reset to default
      setIsModalVisible(false);
      fetchVars();
    } catch (error) {
      console.error('Validation failed:', error);
      message.error('Error saving variable');
    }
  };

  const handleEdit = (record: any) => {
    setEditingKey(record.key);
    const isSecret = Boolean(record.isSecret);
    
    // Set form values including the isSecret flag
    form.setFieldsValue({
      key: record.key,
      value: record.value,
      isSecret: isSecret
    });
    setCurrentIsSecret(isSecret); // Also set the state
    setIsModalVisible(true);
  };

  const handleDelete = async (key: string) => {
    try {
      if (!window.pywebview?.api) return;
      await window.pywebview.api.delete_env_value(key);
      message.success('Variable deleted successfully');
      fetchVars();
    } catch (err) {
      console.error(err);
      message.error('Failed to delete variable');
    }
  };

  const handleBulkSave = async () => {
    try {
      const lines = bulkText.split('\n').filter(line => line.trim());
      const newPairs: Record<string, any> = {};
      lines.forEach(line => {
        const [key, ...valueParts] = line.split('=');
        if (key && valueParts.length > 0) {
          newPairs[key.trim()] = {
            value: valueParts.join('=').trim(),
            is_secret: false,
          };
        }
      });
      if (!window.pywebview?.api) return;
      await window.pywebview.api.bulk_create_env(newPairs);
      message.success(`Added ${Object.keys(newPairs).length} variables`);
      setBulkEditVisible(false);
      setBulkText('');
      fetchVars();
    } catch (error) {
      console.error(error);
      message.error('Invalid format. Use KEY=VALUE format, one per line.');
    }
  };

  const copyToClipboard = () => {
    const envText = variables
      .map(v => `${v.key}=${v.value}`)
      .join('\n');
    navigator.clipboard.writeText(envText);
    message.success('Environment variables copied to clipboard!');
  };

  const maskSecret = (value: string, isSecret: boolean) => {
    if (isSecret && !showSecrets) {
      return '•'.repeat(8);
    }
    return value;
  };

  // Handle switch change
  const handleSecretSwitchChange = (checked: boolean) => {
    console.log('Switch changed to:', checked);
    setCurrentIsSecret(checked);
    // Also update the form value
    form.setFieldsValue({ isSecret: checked });
  };

  // -----------------------------
  // Fetch all variables on mount
  // -----------------------------
  useEffect(() => {
    fetchVars();
  }, []);

  const columns = [
    {
      title: 'Key',
      dataIndex: 'key',
      key: 'key',
      width: '30%',
      render: (text: string, record: any) => (
        <Space>
          <Tag color="blue">{text}</Tag>
          {record.isSecret && <EyeInvisibleOutlined style={{ color: '#ff4d4f' }} />}
        </Space>
      ),
    },
    {
      title: 'Value',
      dataIndex: 'value',
      key: 'value',
      render: (value: string, record: any) => (
        <Text code style={{ fontSize: '12px' }}>
          {maskSecret(value, record.isSecret)}
        </Text>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'isSecret',
      key: 'isSecret',
      width: '100px',
      render: (isSecret: boolean) => (
        <Tag color={isSecret ? 'red' : 'green'}>
          {isSecret ? 'Secret' : 'Plain'}
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: '120px',
      render: (_: any, record: any) => (
        <Space size="small">
          <Tooltip title="Edit">
            <Button
              type="link"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          <Popconfirm
            title="Delete this variable?"
            description="This action cannot be undone."
            onConfirm={() => handleDelete(record.key)}
            okText="Yes"
            cancelText="No"
          >
            <Tooltip title="Delete">
              <Button type="link" danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px' }}>
      <Card>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <div>
            <Title level={3} style={{ margin: 0 }}>
              <CloudServerOutlined style={{ marginRight: 8 }} />
              Environment Variables
            </Title>
            <Text type="secondary">
              Manage environment variables for your application
            </Text>
          </div>
          <Space>
            <Switch
              checkedChildren={<EyeOutlined />}
              unCheckedChildren={<EyeInvisibleOutlined />}
              checked={showSecrets}
              onChange={setShowSecrets}
            />
            <Button icon={<CopyOutlined />} onClick={copyToClipboard}>
              Export
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => {
                setEditingKey(null);
                form.resetFields();
                setCurrentIsSecret(false); // Reset to default
                setIsModalVisible(true);
              }}
            >
              Add Variable
            </Button>
          </Space>
        </div>

        <Alert
          message="Environment variables are securely stored and can be accessed by your application at runtime."
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />

        {/* Variables Table */}
        <Table
          columns={columns}
          dataSource={variables}
          rowKey="key"
          pagination={false}
          size="middle"
          style={{ marginBottom: 24 }}
        />

        <Divider />

        {/* Bulk Actions */}
        <div style={{ textAlign: 'center' }}>
          <Space>
            <Button
              type="dashed"
              onClick={() => setBulkEditVisible(true)}
            >
              Bulk Edit
            </Button>
            <Text type="secondary">
              {variables.length} variable{variables.length !== 1 ? 's' : ''} configured
            </Text>
          </Space>
        </div>
      </Card>

      {/* Add/Edit Variable Modal */}
      <Modal
        title={editingKey ? `Edit ${editingKey}` : 'Add New Variable'}
        open={isModalVisible}
        onOk={handleAdd}
        onCancel={() => {
          setIsModalVisible(false);
          setEditingKey(null);
          form.resetFields();
          setCurrentIsSecret(false);
        }}
        okText={editingKey ? 'Update' : 'Add'}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          style={{ marginTop: 24 }}
          initialValues={{
            isSecret: false
          }}
        >
          <Form.Item
            name="key"
            label="Variable Key"
            rules={[
              { required: true, message: 'Please enter variable key' },
              { pattern: /^[A-Z_][A-Z0-9_]*$/, message: 'Key must contain only uppercase letters, numbers, and underscores' }
            ]}
          >
            <Input
              placeholder="e.g., DATABASE_URL, API_KEY"
              style={{ width: '100%' }}
              disabled={!!editingKey}
            />
          </Form.Item>

          <Form.Item
            name="value"
            label="Variable Value"
            rules={[{ required: true, message: 'Please enter variable value' }]}
          >
            <TextArea
              placeholder="Enter the value for this variable"
              rows={3}
              style={{ width: '100%' }}
            />
          </Form.Item>

          <Form.Item
            name="isSecret"
            label="Security"
            valuePropName="checked"
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Switch 
                checked={currentIsSecret}
                onChange={handleSecretSwitchChange}
              />
              <Text>Treat as secret (value will be masked)</Text>
              <Text type="secondary" style={{ marginLeft: 8 }}>
                Current: {currentIsSecret ? 'Secret' : 'Plain'}
              </Text>
            </div>
          </Form.Item>
        </Form>
        
        {/* Debug info - remove in production */}
        <div style={{ marginTop: 16, padding: 8, background: '#f5f5f5', borderRadius: 4 }}>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            Debug: Form isSecret: {form.getFieldValue('isSecret')?.toString()}, 
            State isSecret: {currentIsSecret.toString()}
          </Text>
        </div>
      </Modal>

      {/* Bulk Edit Modal */}
      <Modal
        title="Bulk Edit Variables"
        open={bulkEditVisible}
        onOk={handleBulkSave}
        onCancel={() => {
          setBulkEditVisible(false);
          setBulkText('');
        }}
        okText="Import"
        width={700}
      >
        <Alert
          message="Enter variables in KEY=VALUE format, one per line. Existing variables with matching keys will be updated."
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />

        <TextArea
          rows={10}
          placeholder={`DATABASE_URL=postgresql://user:pass@localhost:5432/db\nAPI_KEY=sk_1234567890\nDEBUG_MODE=false`}
          value={bulkText}
          onChange={(e) => setBulkText(e.target.value)}
          style={{
            fontFamily: 'monospace',
            fontSize: '14px'
          }}
        />

        <div style={{ marginTop: 8 }}>
          <Text type="secondary">Example format:</Text>
          <pre style={{
            background: '#f5f5f5',
            padding: '8px',
            borderRadius: '4px',
            fontSize: '12px',
            marginTop: '4px'
          }}>
            KEY1=value1{'\n'}KEY2=value2{'\n'}SECRET_KEY=very_secret_value
          </pre>
        </div>
      </Modal>
    </div>
  );
};

export default EnvironmentVariablesForm;