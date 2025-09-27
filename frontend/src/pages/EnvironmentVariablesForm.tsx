import { useState } from 'react';
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
  const [variables, setVariables] = useState([
    { key: 'API_URL', value: 'https://api.example.com', isSecret: false },
    { key: 'DATABASE_URL', value: 'postgresql://user:pass@localhost:5432/db', isSecret: true },
    { key: 'DEBUG_MODE', value: 'false', isSecret: false },
    { key: 'MAX_CONNECTIONS', value: '100', isSecret: false },
  ]);
  const [editingKey, setEditingKey] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [bulkEditVisible, setBulkEditVisible] = useState(false);
  const [bulkText, setBulkText] = useState('');
  const [showSecrets, setShowSecrets] = useState(false);

  const handleAdd = async () => {
    try {
      const values = await form.validateFields();
      const existingIndex = variables.findIndex(v => v.key === values.key);
      
      if (existingIndex > -1 && editingKey !== values.key) {
        message.error('Environment variable with this key already exists');
        return;
      }

      if (editingKey) {
        // Edit existing
        setVariables(variables.map(v => 
          v.key === editingKey ? { ...values } : v
        ));
        message.success('Variable updated successfully');
        setEditingKey(null);
      } else {
        // Add new
        setVariables([...variables, { ...values }]);
        message.success('Variable added successfully');
      }
      
      form.resetFields();
      setIsModalVisible(false);
    } catch (error) {
      console.error('Validation failed:', error);
    }
  };

  const handleEdit = (record:any) => {
    setEditingKey(record.key);
    form.setFieldsValue(record);
    setIsModalVisible(true);
  };

  const handleDelete = (key:any) => {
    setVariables(variables.filter(v => v.key !== key));
    message.success('Variable deleted successfully');
  };

  const handleBulkSave = () => {
    try {
      const lines = bulkText.split('\n').filter(line => line.trim());
      const newVariables:any = [];
      
      lines.forEach(line => {
        const [key, ...valueParts] = line.split('=');
        if (key && valueParts.length > 0) {
          newVariables.push({
            key: key.trim(),
            value: valueParts.join('=').trim(),
            isSecret: false
          });
        }
      });

      setVariables([...variables, ...newVariables]);
      setBulkEditVisible(false);
      setBulkText('');
      message.success(`Added ${newVariables.length} variables`);
    } catch (error) {
      message.error('Invalid format. Use KEY=VALUE format, one per line.');
    }
  };

  const copyToClipboard = () => {
    const envText = variables.map(v => `${v.key}=${v.value}`).join('\n');
    navigator.clipboard.writeText(envText);
    message.success('Environment variables copied to clipboard!');
  };

  const maskSecret = (value:any, isSecret:any) => {
    if (isSecret && !showSecrets) {
      return '•'.repeat(8);
    }
    return value;
  };

  const columns = [
    {
      title: 'Key',
      dataIndex: 'key',
      key: 'key',
      width: '30%',
      render: (text:any, record:any) => (
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
      render: (value:any, record:any) => (
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
      render: (isSecret:any) => (
        <Tag color={isSecret ? 'red' : 'green'}>
          {isSecret ? 'Secret' : 'Plain'}
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: '120px',
      render: (_:any, record:any) => (
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
        }}
        okText={editingKey ? 'Update' : 'Add'}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          style={{ marginTop: 24 }}
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
              <Switch />
              <Text>Treat as secret (value will be masked)</Text>
            </div>
          </Form.Item>
        </Form>
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
            KEY1=value1{'\n'}KEY2=value2{'\n'}SECRET_KEY=very_secret_value</pre>
        </div>
      </Modal>
    </div>
  );
};

export default EnvironmentVariablesForm;