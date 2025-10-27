// src/components/ArduinoTranspilerLog.tsx
import React from 'react';
import { 
  Card, 
  Alert, 
  Progress, 
  Tag, 
  Space, 
  Typography, 
  List, 
  Button, 
  Row,
  Col,
  Statistic,
  Divider
} from 'antd';
import { 
  CheckCircleOutlined, 
  CloseCircleOutlined, 
  WarningOutlined,
  InfoCircleOutlined,
  FileTextOutlined,
  DownloadOutlined,
  ReloadOutlined,
  CloseOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;

interface CompilationResult {
  success: boolean;
  message?: string;
  fileName?: string;
  error?: string;  // Changed from object to string
  warnings?: string[];
  suggestions?: string[];
  specs?: {
    flash: { used: number; total: number };
    ram: { used: number; total: number };
    additional?: { [key: string]: string };
  };
  timestamp?: string;
  errors?: string[]; // Optional: for debugging
}

interface ArduinoTranspilerLogProps {
  compilationResult: CompilationResult;
  onRetry: () => void;
  onDownload: () => void;
  onClose: () => void;
}

const ArduinoTranspilerLog: React.FC<ArduinoTranspilerLogProps> = ({ 
  compilationResult, 
  onRetry, 
  onDownload,
  onClose 
}) => {
  const { 
  success,
  message,
  error,
  warnings = [],
  specs: maybeSpecs,
  suggestions = [],
  timestamp,
  fileName
  } = compilationResult;

  const specs: NonNullable<CompilationResult["specs"]> = maybeSpecs ?? {
    flash: { used: 0, total: 0 },
    ram: { used: 0, total: 0 },
    additional: {}
  };


  // Calculate memory usage percentages
  const flashUsage = specs.flash ? (specs.flash.used / specs.flash.total) * 100 : 0;
  const ramUsage = specs.ram ? (specs.ram.used / specs.ram.total) * 100 : 0;

  const getMemoryStatus = (usage: number): "success" | "normal" | "exception" => {
    if (usage < 70) return 'success';
    if (usage < 90) return 'normal';
    return 'exception';
  };

  return (
    <Card 
      style={{ 
        marginBottom: 12,
        border: success ? '1px solid #52c41a' : '1px solid #ff4d4f'
      }}
      bodyStyle={{ padding: 0 }}
    >
      {/* Header */}
      <div 
        style={{ 
          padding: '12px 16px',
          background: success ? '#f6ffed' : '#fff2f0',
          borderBottom: `1px solid ${success ? '#b7eb8f' : '#ffccc7'}`
        }}
      >
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              {success ? (
                <CheckCircleOutlined style={{ color: '#52c41a', fontSize: '18px' }} />
              ) : (
                <CloseCircleOutlined style={{ color: '#ff4d4f', fontSize: '18px' }} />
              )}
              <Title level={5} style={{ margin: 0 }}>
                {success ? 'Compilation Successful!' : 'Compilation Failed'}
              </Title>
              {fileName && (
                <Tag icon={<FileTextOutlined />} color="blue">
                  {fileName}
                </Tag>
              )}
            </Space>
          </Col>
          <Col>
            <Space>
              <Button 
                icon={<ReloadOutlined />} 
                onClick={onRetry}
                size="small"
              >
                Retry
              </Button>
              {success && (
                <Button 
                  type="primary" 
                  icon={<DownloadOutlined />} 
                  onClick={onDownload}
                  size="small"
                >
                  Download HEX
                </Button>
              )}
              <Button 
                icon={<CloseOutlined />} 
                onClick={onClose}
                size="small"
                type="text"
              />
            </Space>
          </Col>
        </Row>
      </div>

      {/* Main Content */}
      <div style={{ padding: '16px' }}>
        {success ? (
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            {/* Success Message */}
            <Alert
              message={message || "Your Arduino code has been successfully transpiled and compiled!"}
              type="success"
              showIcon
            />

            {/* Memory Usage Stats */}
            {specs.flash && specs.ram && (
              <div>
                <Title level={5}>Memory Usage</Title>
                <Row gutter={16}>
                  <Col span={12}>
                    <Card size="small">
                      <Statistic
                        title="Flash Memory"
                        value={specs.flash.used}
                        suffix={`/ ${specs.flash.total} bytes`}
                        valueStyle={{ 
                          color: getMemoryStatus(flashUsage) === 'success' ? '#3f8600' : 
                                getMemoryStatus(flashUsage) === 'normal' ? '#faad14' : '#cf1322'
                        }}
                      />
                      <Progress 
                        percent={Math.round(flashUsage)} 
                        status={getMemoryStatus(flashUsage)}
                        showInfo={false}
                        style={{ marginTop: 8 }}
                      />
                      <Text type="secondary">
                        {Math.round(flashUsage)}% used
                      </Text>
                    </Card>
                  </Col>
                  <Col span={12}>
                    <Card size="small">
                      <Statistic
                        title="RAM Usage"
                        value={specs.ram.used}
                        suffix={`/ ${specs.ram.total} bytes`}
                        valueStyle={{ 
                          color: getMemoryStatus(ramUsage) === 'success' ? '#3f8600' : 
                                getMemoryStatus(ramUsage) === 'normal' ? '#faad14' : '#cf1322'
                        }}
                      />
                      <Progress 
                        percent={Math.round(ramUsage)} 
                        status={getMemoryStatus(ramUsage)}
                        showInfo={false}
                        style={{ marginTop: 8 }}
                      />
                      <Text type="secondary">
                        {Math.round(ramUsage)}% used
                      </Text>
                    </Card>
                  </Col>
                </Row>
              </div>
            )}

            {/* Additional Specs */}
            {specs.additional && Object.keys(specs.additional).length > 0 && (
              <div>
                <Title level={5}>Additional Information</Title>
                <Space wrap>
                  {Object.entries(specs.additional).map(([key, value]) => (
                    <Tag key={key} color="blue">
                      {key}: {value}
                    </Tag>
                  ))}
                </Space>
              </div>
            )}

            {/* Warnings */}
            {warnings.length > 0 && (
              <div>
                <Title level={5}>
                  <WarningOutlined style={{ color: '#faad14' }} /> 
                  Warnings ({warnings.length})
                </Title>
                <List
                  size="small"
                  dataSource={warnings}
                  /*renderItem={(warning, index) => (
                    <List.Item>
                      <Space>
                        <WarningOutlined style={{ color: '#faad14' }} />
                        <Text>{warning}</Text>
                      </Space>
                    </List.Item>
                  )}*/
                />
              </div>
            )}
          </Space>
        ) : (
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            {/* Error Message */}
            <Alert
              message={error || message || 'Compilation failed'}
              type="error"
              showIcon
            />

            {/* Error Details */}
            {error && (
              <Card size="small" title="Error Details">
                <Text 
                  type="danger" 
                  style={{ 
                    whiteSpace: 'pre-wrap', 
                    fontFamily: 'monospace', 
                    fontSize: '12px',
                    display: 'block'
                  }}
                >
                  {error}
                </Text>
              </Card>
            )}

            {/* Suggestions */}
            {suggestions.length > 0 && (
              <div>
                <Title level={5}>
                  <InfoCircleOutlined style={{ color: '#1890ff' }} /> 
                  Suggestions
                </Title>
                <List
                  size="small"
                  dataSource={suggestions}
                  renderItem={(suggestion, _) => (
                    <List.Item>
                      <Space>
                        <InfoCircleOutlined style={{ color: '#1890ff' }} />
                        <Text>{suggestion}</Text>
                      </Space>
                    </List.Item>
                  )}
                />
              </div>
            )}

            {/* Warnings (show even on failure) */}
            {warnings.length > 0 && (
              <div>
                <Title level={5}>
                  <WarningOutlined style={{ color: '#faad14' }} /> 
                  Warnings ({warnings.length})
                </Title>
                <List
                  size="small"
                  dataSource={warnings}
                  renderItem={(warning, _) => (
                    <List.Item>
                      <Space>
                        <WarningOutlined style={{ color: '#faad14' }} />
                        <Text>{warning}</Text>
                      </Space>
                    </List.Item>
                  )}
                />
              </div>
            )}
          </Space>
        )}

        {/* Timestamp */}
        {timestamp && (
          <>
            <Divider style={{ margin: '16px 0' }} />
            <Text type="secondary" style={{ fontSize: '12px' }}>
              Compiled at: {new Date(timestamp).toLocaleString()}
            </Text>
          </>
        )}
      </div>
    </Card>
  );
};

export default ArduinoTranspilerLog;