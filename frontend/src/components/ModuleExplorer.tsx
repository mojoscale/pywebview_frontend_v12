// src/components/ModuleExplorer.tsx
import { useEffect, useState, useMemo } from "react";
import {
  Input,
  Collapse,
  Typography,
  List,
  Card,
  Tabs,
  Switch,
  Tag,
  Button,
  Space,
  Badge,
  Avatar,
  Empty,
  Modal,
  message,
} from "antd";
import {
  FileSearchOutlined,
  MoonOutlined,
  SunOutlined,
  FunctionOutlined,
  CrownOutlined,
  CodeOutlined,
  ApiOutlined,
  SearchOutlined,
  CopyOutlined,
  EyeOutlined,
} from "@ant-design/icons";
import Fuse from "fuse.js";

type FunctionEntry = { name: string; signature: string; doc: string };
type ClassEntry = { name: string; doc: string; methods?: FunctionEntry[] };
type VariableEntry = { name: string; value: string; doc?: string };
type ModuleEntry = {
  functions?: FunctionEntry[];
  classes?: ClassEntry[];
  variables?: VariableEntry[];
  doc?: string;
};

// Explorer item type
type ExplorerItem =
  | (FunctionEntry & { type: "function"; module: string })
  | (ClassEntry & { type: "class"; module: string })
  | (FunctionEntry & { type: "method"; module: string; parentClass: string })
  | (VariableEntry & { type: "variable"; module: string });

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

const ModuleExplorer = () => {
  const [rawModules, setRawModules] = useState<Record<string, ModuleEntry>>({});
  const [search, setSearch] = useState("");
  const [darkMode, setDarkMode] = useState(false);
  const [activePanels, setActivePanels] = useState<string[]>([]);
  const [detailModal, setDetailModal] = useState<{
    visible: boolean;
    item: ExplorerItem | null;
  }>({
    visible: false,
    item: null,
  });

  // Process module data to handle classes specially
  const processedModules = useMemo(() => {
    const processed: Record<string, ModuleEntry> = JSON.parse(JSON.stringify(rawModules));
    
    Object.entries(processed).forEach(([modName, mod]) => {
      if (mod.classes) {
        mod.classes = mod.classes.map(cls => {
          // Look for __init__ method to get class doc and signature
          const initMethod = cls.methods?.find(m => m.name === '__init__');
          let classDoc = '';
          let classSignature = '';
          
          if (initMethod) {
            // ALWAYS use __init__ docstring for class, ignore class doc completely
            classDoc = initMethod.doc || '';
            
            // Extract signature from __init__, remove 'self' parameter
            if (initMethod.signature) {
              // Remove 'self' and any following comma, handle different signature formats
              classSignature = initMethod.signature
                .replace(/\(self\s*,?\s*/, '(') // Remove self with possible comma
                .replace(/\(self\)/, '()'); // Handle case with only self parameter
              
              // Ensure we have proper formatting
              if (!classSignature.startsWith('(')) {
                classSignature = `(${classSignature}`;
              }
              if (!classSignature.endsWith(')')) {
                classSignature = `${classSignature})`;
              }
            }
            
            // Remove __init__ from methods list since we're using it for the class
            cls.methods = cls.methods?.filter(m => m.name !== '__init__');
          }
          
          return {
            ...cls,
            doc: classDoc, // Always use __init__ doc (could be empty string)
            signature: classSignature || '()', // Default to empty parentheses
          };
        });
      }
    });
    
    return processed;
  }, [rawModules]);

  // Load module data from backend
  useEffect(() => {
    (async () => {
      try {
        const result = await (window as any).pywebview.api.get_module_index();
        if (result && typeof result === "object") {
          const data = "data" in result ? result.data : result;
          setRawModules(data);
        }
      } catch (e) {
        console.error("❌ Could not load module index", e);
      }
    })();
  }, []);

  // Create hierarchical items for display (not flattened)
  const getModuleItems = (modName: string, mod: ModuleEntry): ExplorerItem[] => {
    const items: ExplorerItem[] = [];
    
    // Add functions
    mod.functions?.forEach((fn) => {
      items.push({
        module: modName,
        type: "function",
        ...fn,
      });
    });
    
    // Add classes with their methods
    mod.classes?.forEach((cls) => {
      // Add the class itself
      items.push({
        module: modName,
        type: "class",
        ...cls,
      });
      
      // Add class methods right after the class
      cls.methods?.forEach((method) => {
        items.push({
          module: modName,
          type: "method",
          parentClass: cls.name,
          ...method,
        });
      });
    });
    
    // Add variables
    mod.variables?.forEach((v) => {
      items.push({
        module: modName,
        type: "variable",
        ...v,
      });
    });
    
    return items;
  };

  // Flatten for search only
  const flattened: ExplorerItem[] = useMemo(() => {
    const list: ExplorerItem[] = [];
    Object.entries(processedModules).forEach(([modName, mod]) => {
      list.push(...getModuleItems(modName, mod));
    });
    return list;
  }, [processedModules]);

  // Search with fuse
  const searchResults = useMemo(() => {
    if (!search.trim()) {
      return {
        modules: processedModules,
        flattened: flattened,
        hasSearch: false,
      };
    }

    const fuse = new Fuse(flattened, {
      keys: ["name", "module", "signature", "doc", "parentClass", "value"],
      threshold: 0.3,
      includeScore: true,
      ignoreLocation: true,
      minMatchCharLength: 2,
    });

    const searchResults = fuse.search(search);
    const resultItems = searchResults.map((r) => r.item);

    // Group results by module for display
    const groupedResults: Record<string, ExplorerItem[]> = {};
    resultItems.forEach((item) => {
      if (!groupedResults[item.module]) {
        groupedResults[item.module] = [];
      }
      groupedResults[item.module].push(item);
    });

    return {
      modules: groupedResults,
      flattened: resultItems,
      hasSearch: true,
    };
  }, [search, flattened, processedModules]);

  // Get type icon and color
  const getTypeConfig = (type: string) => {
    switch (type) {
      case "function":
        return {
          icon: <FunctionOutlined />,
          color: "#1890ff",
          label: "Function",
        };
      case "class":
        return { icon: <CrownOutlined />, color: "#52c41a", label: "Class" };
      case "method":
        return { icon: <CodeOutlined />, color: "#722ed1", label: "Method" };
      case "variable":
        return { icon: <ApiOutlined />, color: "#fa8c16", label: "Variable" };
      default:
        return { icon: <CodeOutlined />, color: "#8c8c8c", label: "Unknown" };
    }
  };

  // Copy to clipboard
  const copyToClipboard = async (text: string, description: string) => {
    try {
      await navigator.clipboard.writeText(text);
      message.success(`Copied ${description} to clipboard!`);
    } catch (err) {
      message.error('Failed to copy to clipboard');
    }
  };

  // Show detail modal
  const showDetailModal = (item: ExplorerItem) => {
    setDetailModal({
      visible: true,
      item,
    });
  };

  // Get display name for item
  const getDisplayName = (item: ExplorerItem): string => {
    if (item.type === "method") {
      return `${item.parentClass}.${item.name}`;
    }
    return item.name;
  };

  // Get copyable content for item
  const getCopyableContent = (item: ExplorerItem): string => {
    switch (item.type) {
      case "function":
        return `${item.name}${item.signature}`;
      case "method":
        // For methods, remove 'self' from signature if present
        const methodSignature = item.signature.replace(/\(self\s*,?\s*/, '(').replace(/\(self\)/, '()');
        return `${item.parentClass}.${item.name}${methodSignature}`;
      case "class":
        return `${item.name}${item.signature}`;
      case "variable":
        return item.name;
      default:
        return item.name;
    }
  };

  // Render entry card
  const renderEntry = (item: ExplorerItem) => {
    const typeConfig = getTypeConfig(item.type);
    const displayName = getDisplayName(item);
    const copyableContent = getCopyableContent(item);

    return (
      <Card
        size="small"
        hoverable
        style={{
          marginBottom: 8,
          border: `1px solid ${darkMode ? "#434343" : "#f0f0f0"}`,
          borderRadius: 6,
          background: darkMode ? "rgba(255,255,255,0.02)" : "#fff",
          cursor: "pointer",
        }}
        bodyStyle={{ padding: 12 }}
        onClick={() => showDetailModal(item)}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {/* Header */}
          <div style={{ 
            display: "flex", 
            alignItems: "flex-start", 
            gap: 8,
            minHeight: 24
          }}>
            <Avatar
              size="small"
              icon={typeConfig.icon}
              style={{
                backgroundColor: typeConfig.color,
                fontSize: 12,
                flexShrink: 0,
              }}
            />
            
            <div style={{ 
              flex: 1, 
              minWidth: 0,
              display: "flex", 
              flexDirection: "column", 
              gap: 4 
            }}>
              {/* Name and signature row */}
              <div style={{ 
                display: "flex", 
                alignItems: "center", 
                gap: 8,
                flexWrap: "wrap" 
              }}>
                <Text
                  strong
                  style={{ 
                    color: darkMode ? "#fff" : "#000", 
                    fontSize: 13,
                    lineHeight: 1.2
                  }}
                  onClick={(e) => {
                    e.stopPropagation();
                    copyToClipboard(displayName, "name");
                  }}
                >
                  {displayName}
                </Text>
                
                {"signature" in item && item.signature && item.signature !== '()' && (
                  <Tag
                    color={darkMode ? "blue" : "geekblue"}
                    style={{ 
                      margin: 0, 
                      fontSize: 10, 
                      lineHeight: 1.2,
                      flexShrink: 0 
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      copyToClipboard(item.signature, "signature");
                    }}
                  >
                    {item.signature}
                  </Tag>
                )}
              </div>
              
              {/* Type and module row */}
              <div style={{ 
                display: "flex", 
                alignItems: "center", 
                gap: 8,
                justifyContent: "space-between"
              }}>
                <Tag
                  style={{
                    fontSize: 9,
                    padding: "1px 6px",
                    border: `1px solid ${typeConfig.color}20`,
                    color: typeConfig.color,
                    background: `${typeConfig.color}10`,
                    lineHeight: 1.2,
                    margin: 0
                  }}
                >
                  {typeConfig.label}
                </Tag>
                
                <Text 
                  type="secondary" 
                  style={{ 
                    fontSize: 10,
                    lineHeight: 1.2
                  }}
                  onClick={(e) => {
                    e.stopPropagation();
                    copyToClipboard(item.module, "module path");
                  }}
                >
                  {item.module}
                </Text>
              </div>
            </div>
            
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              style={{ 
                flexShrink: 0,
                marginLeft: 4 
              }}
              onClick={(e) => {
                e.stopPropagation();
                showDetailModal(item);
              }}
            />
          </div>

          {/* Documentation */}
          {"doc" in item && item.doc && (
            <Paragraph
              style={{
                margin: 0,
                fontSize: 12,
                lineHeight: 1.4,
                color: darkMode ? "#8c8c8c" : "#666",
              }}
              ellipsis={{ rows: 2, expandable: true }}
            >
              {item.doc}
            </Paragraph>
          )}

          {/* Variable value */}
          {"value" in item && item.value && (
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <Text 
                style={{ 
                  fontSize: 11, 
                  color: darkMode ? "#8c8c8c" : "#666",
                  fontWeight: 500 
                }}
              >
                Value:
              </Text>
              <Tag
                color={darkMode ? "blue" : "cyan"}
                style={{ 
                  margin: 0, 
                  fontSize: 10,
                  lineHeight: 1.2
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  copyToClipboard(item.value, "value");
                }}
              >
                {item.value}
              </Tag>
            </div>
          )}
        </div>
      </Card>
    );
  };

  // Render detail modal
  const renderDetailModal = () => {
    if (!detailModal.item) return null;

    const item = detailModal.item;
    const typeConfig = getTypeConfig(item.type);
    const displayName = getDisplayName(item);
    const copyableContent = getCopyableContent(item);

    return (
      <Modal
        title={
          <Space>
            <Avatar
              size="small"
              icon={typeConfig.icon}
              style={{
                backgroundColor: typeConfig.color,
              }}
            />
            <Text strong>{displayName}</Text>
            <Tag color={typeConfig.color}>{typeConfig.label}</Tag>
          </Space>
        }
        open={detailModal.visible}
        onCancel={() => setDetailModal({ visible: false, item: null })}
        footer={[
          <Button
            key="copy"
            type="primary"
            icon={<CopyOutlined />}
            onClick={() => copyToClipboard(copyableContent, displayName)}
          >
            Copy {item.type === "function" || item.type === "method" || item.type === "class" ? "Signature" : "Name"}
          </Button>,
          <Button
            key="close"
            onClick={() => setDetailModal({ visible: false, item: null })}
          >
            Close
          </Button>,
        ]}
        width={600}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* Basic info */}
          <div>
            <Text strong>Module: </Text>
            <Text 
              code 
              style={{ cursor: "pointer" }}
              onClick={() => copyToClipboard(item.module, "module path")}
            >
              {item.module}
            </Text>
          </div>

          {/* Signature for functions/methods/classes */}
          {"signature" in item && item.signature && item.signature !== '()' && (
            <div>
              <Text strong>Signature: </Text>
              <Text 
                code 
                style={{ 
                  cursor: "pointer",
                  background: darkMode ? "#2a2a2a" : "#f5f5f5",
                  padding: "2px 6px",
                  borderRadius: 3,
                }}
                onClick={() => copyToClipboard(
                  item.type === "class" ? `${item.name}${item.signature}` : `${item.name}${item.signature}`, 
                  "signature"
                )}
              >
                {item.type === "class" ? `${item.name}${item.signature}` : `${item.name}${item.signature}`}
              </Text>
            </div>
          )}

          {/* Value for variables */}
          {"value" in item && item.value && (
            <div>
              <Text strong>Value: </Text>
              <Text 
                code 
                style={{ 
                  cursor: "pointer",
                  background: darkMode ? "#2a2a2a" : "#f5f5f5",
                  padding: "2px 6px",
                  borderRadius: 3,
                }}
                onClick={() => copyToClipboard(item.value, "value")}
              >
                {item.value}
              </Text>
            </div>
          )}

          {/* Documentation */}
          {"doc" in item && item.doc && (
            <div>
              <Text strong>Documentation:</Text>
              <div
                style={{
                  marginTop: 8,
                  padding: 12,
                  background: darkMode ? "#1f1f1f" : "#f9f9f9",
                  borderRadius: 4,
                  border: `1px solid ${darkMode ? "#303030" : "#e8e8e8"}`,
                }}
              >
                <Paragraph
                  style={{
                    margin: 0,
                    whiteSpace: "pre-wrap",
                    fontSize: 13,
                    lineHeight: 1.5,
                  }}
                >
                  {item.doc}
                </Paragraph>
              </div>
            </div>
          )}
        </div>
      </Modal>
    );
  };

  const displayModules = searchResults.hasSearch
    ? searchResults.modules
    : processedModules;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        background: darkMode ? "#141414" : "#fafafa",
        borderRadius: 8,
        overflow: "hidden",
        border: `1px solid ${darkMode ? "#303030" : "#e8e8e8"}`,
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "16px 20px",
          borderBottom: `1px solid ${darkMode ? "#303030" : "#f0f0f0"}`,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          background: darkMode ? "#1f1f1f" : "#fff",
          flexShrink: 0,
        }}
      >
        <Space>
          <FileSearchOutlined
            style={{ color: darkMode ? "#177ddc" : "#1890ff", fontSize: 18 }}
          />
          <Title
            level={5}
            style={{ margin: 0, color: darkMode ? "#fff" : "#000" }}
          >
            Module Explorer
          </Title>
          <Badge
            count={Object.keys(processedModules).length}
            size="small"
            color={darkMode ? "#177ddc" : "#1890ff"}
          />
        </Space>
        <Space>
          <Text
            style={{ fontSize: 12, color: darkMode ? "#8c8c8c" : "#666" }}
          >
            {darkMode ? "Dark" : "Light"}
          </Text>
          <Switch
            checkedChildren={<MoonOutlined />}
            unCheckedChildren={<SunOutlined />}
            checked={darkMode}
            onChange={setDarkMode}
            size="small"
          />
        </Space>
      </div>

      {/* Search */}
      <div
        style={{
          padding: 16,
          background: darkMode ? "#141414" : "#fafafa",
          flexShrink: 0,
          borderBottom: `1px solid ${darkMode ? "#303030" : "#f0f0f0"}`,
        }}
      >
        <Input
          placeholder="Search functions, classes, methods, variables..."
          allowClear
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          prefix={<SearchOutlined />}
          style={{
            background: darkMode ? "#1f1f1f" : "#fff",
          }}
          size="middle"
        />
        {searchResults.hasSearch && (
          <Text
            style={{
              fontSize: 12,
              color: darkMode ? "#8c8c8c" : "#666",
              marginTop: 8,
              display: "block",
            }}
          >
            Found {searchResults.flattened.length} results
          </Text>
        )}
      </div>

      {/* Main Content */}
      <div
        style={{
          flex: 1,
          overflow: "auto",
          minHeight: 0,
        }}
      >
        <div style={{ padding: "0 16px 16px 16px" }}>
          {Object.keys(displayModules).length === 0 ? (
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description={
                search ? "No results found" : "No modules available"
              }
              style={{
                margin: "40px 0",
                color: darkMode ? "#666" : "#999",
              }}
            />
          ) : (
            <Collapse
              accordion
              ghost
              activeKey={activePanels}
              onChange={(keys) =>
                setActivePanels(Array.isArray(keys) ? keys : [keys])
              }
              style={{ background: "transparent" }}
            >
              {Object.entries(displayModules).map(([modName, mod]) => {
                const items = searchResults.hasSearch
                  ? (mod as ExplorerItem[])
                  : getModuleItems(modName, mod as ModuleEntry);

                return (
                  <Panel
                    header={
                      <Space>
                        <Text
                          strong
                          style={{
                            color: darkMode ? "#fff" : "#000",
                          }}
                        >
                          {modName}
                        </Text>
                        <Badge
                          count={items.length}
                          size="small"
                          color={darkMode ? "blue" : "geekblue"}
                        />
                      </Space>
                    }
                    key={modName}
                    style={{
                      border: `1px solid ${
                        darkMode ? "#303030" : "#f0f0f0"
                      }`,
                      borderRadius: 6,
                      marginBottom: 8,
                      background: darkMode ? "#1f1f1f" : "#fff",
                    }}
                  >
                    <List
                      dataSource={items}
                      renderItem={(item: ExplorerItem) => (
                        <List.Item style={{ padding: "4px 0" }}>
                          {renderEntry(item)}
                        </List.Item>
                      )}
                      locale={{ emptyText: "No items found" }}
                    />
                  </Panel>
                );
              })}
            </Collapse>
          )}
        </div>
      </div>

      {/* Detail Modal */}
      {renderDetailModal()}
    </div>
  );
};

export default ModuleExplorer;