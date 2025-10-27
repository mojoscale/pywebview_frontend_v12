// src/components/ModuleExplorer.tsx
import { useEffect, useState, useMemo } from "react";
import {
  Input,
  Collapse,
  Typography,
  List,
  Card,
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
  FileTextOutlined,
  FolderOutlined,
} from "@ant-design/icons";
import Fuse from "fuse.js";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { 
  vscDarkPlus,
  vs 
} from 'react-syntax-highlighter/dist/esm/styles/prism';

type FunctionEntry = { name: string; signature: string; doc: string };
type ClassEntry = { name: string; doc: string; signature: string; methods?: FunctionEntry[] };
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
  | (VariableEntry & { type: "variable"; module: string })
  | { type: "module"; module: string; doc: string };

// Code block type
type CodeBlock = {
  language: string;
  code: string;
};

// Folder structure type
type FolderStructure = {
  name: string;
  modules: Record<string, ModuleEntry>;
  subFolders?: Record<string, FolderStructure>;
};

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

// Helper function to parse docstrings for code blocks
const parseDocstringForCodeBlocks = (doc: string): { description: string; codeBlocks: CodeBlock[] } => {
  if (!doc) return { description: '', codeBlocks: [] };
  
  const codeBlockRegex = /```(\w+)?\s*\n([\s\S]*?)```/g;
  const codeBlocks: CodeBlock[] = [];
  let cleanDoc = doc;
  
  // Extract code blocks
  let match;
  while ((match = codeBlockRegex.exec(doc)) !== null) {
    const language = match[1] || 'python';
    const code = match[2].trim();
    codeBlocks.push({ language, code });
    
    // Remove the code block from the description to avoid duplication
    cleanDoc = cleanDoc.replace(match[0], '');
  }
  
  // Clean up extra newlines and whitespace
  cleanDoc = cleanDoc.trim().replace(/\n\s*\n\s*\n/g, '\n\n');
  
  return { description: cleanDoc, codeBlocks };
};

// Helper to organize modules into folder structure
const organizeModulesByFolder = (modules: Record<string, ModuleEntry>): FolderStructure => {
  const root: FolderStructure = {
    name: "root",
    modules: {},
    subFolders: {},
  };

  Object.entries(modules).forEach(([modPath, modEntry]) => {
    // Split by dots: sensor.xxx -> ["sensor", "xxx"]
    const parts = modPath.split(".");
    const isBarModule = parts.length === 1; // No dots, just bare module name

    if (isBarModule) {
      // Bare module - goes directly to root
      root.modules[modPath] = modEntry;
    } else {
      // Module with dots - organize into structure
      let current = root;
      
      // Navigate/create folder structure for all but the last part
      for (let i = 0; i < parts.length - 1; i++) {
        const folderName = parts[i];
        if (!current.subFolders) current.subFolders = {};
        if (!current.subFolders[folderName]) {
          current.subFolders[folderName] = {
            name: folderName,
            modules: {},
            subFolders: {},
          };
        }
        current = current.subFolders[folderName];
      }
      
      // Add module to final folder with just the last part as display name
      current.modules[modPath] = modEntry;
    }
  });

  return root;
};

const ModuleExplorer = () => {
  const [rawModules, setRawModules] = useState<Record<string, ModuleEntry>>({});
  const [search, setSearch] = useState("");
  const [darkMode, setDarkMode] = useState(false);
  const [expandedFolders, setExpandedFolders] = useState<string[]>([]);
  const [expandedModules, setExpandedModules] = useState<string[]>([]);
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
    
    Object.entries(processed).forEach(([_, mod]) => {
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
    
    // Add module docstring as first item if it exists
    if (mod.doc) {
      items.push({
        module: modName,
        type: "module",
        doc: mod.doc,
      });
    }
    
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

  // Flatten for search only (excluding module docs for search)
  const flattened: ExplorerItem[] = useMemo(() => {
    const list: ExplorerItem[] = [];
    Object.entries(processedModules).forEach(([modName, mod]) => {
      // Only include actual code items in search, not module docs
      const items = getModuleItems(modName, mod).filter(item => item.type !== "module");
      list.push(...items);
    });
    return list;
  }, [processedModules]);

  // Helper to get display content for signature
  const getSignatureDisplay = (item: ExplorerItem, signature: string | null): string => {
    if (!signature) return "";
    
    if (item.type === "module") {
      return signature;
    }
    
    // For items with names (functions, methods, classes)
    if ("name" in item) {
      return `${item.name}${signature}`;
    }
    
    return signature;
  };

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
      keys: ["name", "module", "doc", "signature"],
      threshold: 0.3,
      minMatchCharLength: 1,
    });

    const results = fuse.search(search).map(r => r.item);
    
    // Build module map from search results
    const resultModules: Record<string, ModuleEntry> = {};
    results.forEach((item) => {
      if (item.type !== "module" && "name" in item) {
        if (!resultModules[item.module]) {
          resultModules[item.module] = processedModules[item.module];
        }
      }
    });

    return {
      modules: resultModules,
      flattened: results,
      hasSearch: true,
    };
  }, [search, flattened, processedModules]);

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    message.success(`${label} copied to clipboard`);
  };

  // Get icon for item type
  const getItemIcon = (type: string, darkMode: boolean) => {
    const color = darkMode ? "#177ddc" : "#1890ff";
    switch (type) {
      case "function":
      case "method":
        return <FunctionOutlined style={{ color, marginRight: 8 }} />;
      case "class":
        return <CrownOutlined style={{ color, marginRight: 8 }} />;
      case "variable":
        return <CodeOutlined style={{ color, marginRight: 8 }} />;
      case "module":
        return <ApiOutlined style={{ color, marginRight: 8 }} />;
      default:
        return null;
    }
  };

  // Render a single entry
  const renderEntry = (item: ExplorerItem) => {
    const displayStyle = {
      padding: "8px 12px",
      cursor: "pointer",
      borderRadius: 4,
      transition: "background-color 0.2s",
      color: darkMode ? "#d9d9d9" : "#333",
      fontSize: 13,
    };

    const itemLabel = "name" in item ? item.name : item.module;
    const signature = "signature" in item ? item.signature : null;

    const hoverStyle = {
      ...displayStyle,
      background: darkMode ? "#262626" : "#f5f5f5",
    };

    return (
      <div
        style={displayStyle}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLElement).style.background = darkMode ? "#262626" : "#f5f5f5";
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLElement).style.background = "transparent";
        }}
        onClick={() => {
          setDetailModal({ visible: true, item });
        }}
      >
        <Space size={8}>
          {getItemIcon(item.type, darkMode)}
          <div style={{ display: "flex", flexDirection: "column" }}>
            <div style={{ fontSize: 13, fontWeight: 500 }}>
              {itemLabel}
              {item.type === "method" && (
                <span style={{ fontSize: 11, color: darkMode ? "#8c8c8c" : "#999", marginLeft: 8 }}>
                  (method of {item.parentClass})
                </span>
              )}
            </div>
            {signature && (
              <div
                style={{
                  fontSize: 11,
                  fontFamily: "monospace",
                  color: darkMode ? "#8c8c8c" : "#666",
                  marginTop: 2,
                }}
              >
                {getSignatureDisplay(item, signature)}
              </div>
            )}
          </div>
          <Tag
            size="small"
            style={{ marginLeft: "auto", fontSize: 10 }}
            color={
              item.type === "function" || item.type === "method"
                ? "blue"
                : item.type === "class"
                ? "purple"
                : item.type === "variable"
                ? "green"
                : "default"
            }
          >
            {item.type}
          </Tag>
        </Space>
      </div>
    );
  };

  // Render module items within a module panel
  const renderModuleItems = (modName: string, mod: ModuleEntry) => {
    const items = getModuleItems(modName, mod);
    
    return (
      <List
        dataSource={items}
        renderItem={(item: ExplorerItem) => (
          <List.Item style={{ padding: "4px 0" }}>
            {renderEntry(item)}
          </List.Item>
        )}
        locale={{ emptyText: "No items found" }}
      />
    );
  };

  // Render folder structure recursively
  const renderFolderStructure = (folder: FolderStructure, path: string = "") => {
    const items = [];
    
    // Render subfolders
    if (folder.subFolders) {
      Object.entries(folder.subFolders).forEach(([folderName, subFolder]) => {
        const folderPath = path ? `${path}/${folderName}` : folderName;
        const folderKey = `folder-${folderPath}`;
        
        // Count total items in folder (including subfolders)
        const countItems = (f: FolderStructure): number => {
          let count = Object.keys(f.modules).reduce((acc, modName) => {
            const mod = f.modules[modName];
            return acc + getModuleItems(modName, mod).filter(i => i.type !== "module").length;
          }, 0);
          
          if (f.subFolders) {
            count += Object.values(f.subFolders).reduce((acc, sf) => acc + countItems(sf), 0);
          }
          
          return count;
        };
        
        items.push(
          <Panel
            key={folderKey}
            header={
              <Space>
                <FolderOutlined style={{ color: darkMode ? "#fadb14" : "#ffc069" }} />
                <Text strong style={{ color: darkMode ? "#fff" : "#000" }}>
                  {folderName}
                </Text>
                <Badge
                  count={countItems(subFolder)}
                  size="small"
                  color={darkMode ? "blue" : "geekblue"}
                />
              </Space>
            }
            style={{
              border: `1px solid ${darkMode ? "#303030" : "#f0f0f0"}`,
              borderRadius: 6,
              marginBottom: 8,
              background: darkMode ? "#1f1f1f" : "#fff",
            }}
          >
            <Collapse
              accordion
              ghost
              style={{ background: "transparent" }}
            >
              {renderFolderStructure(subFolder, folderPath)}
            </Collapse>
          </Panel>
        );
      });
    }
    
    // Render modules in this folder
    Object.entries(folder.modules).forEach(([modName, mod]) => {
      const moduleKey = `module-${modName}`;
      const items_count = getModuleItems(modName, mod).filter(i => i.type !== "module").length;
      
      items.push(
        <Panel
          key={moduleKey}
          header={
            <Space>
              <CodeOutlined style={{ color: darkMode ? "#177ddc" : "#1890ff" }} />
              <Text style={{ color: darkMode ? "#fff" : "#000" }}>
                {modName.split(".").pop()}
              </Text>
              <Badge
                count={items_count}
                size="small"
                color={darkMode ? "cyan" : "geekblue"}
              />
            </Space>
          }
          style={{
            border: `1px solid ${darkMode ? "#303030" : "#f0f0f0"}`,
            borderRadius: 6,
            marginBottom: 8,
            marginLeft: 16,
            background: darkMode ? "#1f1f1f" : "#fff",
          }}
        >
          {renderModuleItems(modName, mod)}
        </Panel>
      );
    });
    
    return items;
  };

  // Render detail modal
  const renderDetailModal = () => {
    if (!detailModal.item) return null;

    const item = detailModal.item;
    const docContent = parseDocstringForCodeBlocks(item.doc || "");

    return (
      <Modal
        title={
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            {getItemIcon(item.type, darkMode)}
            <span>
              {"name" in item ? item.name : item.module}
            </span>
            <Tag color={item.type === "method" ? "blue" : item.type === "class" ? "purple" : "default"}>
              {item.type}
            </Tag>
          </div>
        }
        open={detailModal.visible}
        onCancel={() => setDetailModal({ visible: false, item: null })}
        footer={null}
        width={800}
        style={{
          colorScheme: darkMode ? "dark" : "light",
        }}
        bodyStyle={{
          background: darkMode ? "#141414" : "#fff",
          color: darkMode ? "#fff" : "#000",
        }}
      >
        <div style={{ marginBottom: 16 }}>
          {/* Signature */}
          {item.type !== "module" && (
            <div style={{ marginBottom: 16 }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: 8,
                }}
              >
                <Text strong style={{ fontSize: 12, color: darkMode ? "#8c8c8c" : "#666" }}>
                  SIGNATURE
                </Text>
                <Button
                  size="small"
                  type="text"
                  icon={<CopyOutlined />}
                  onClick={() => {
                    const sig = "signature" in item ? item.signature : "";
                    const display = getSignatureDisplay(item, sig);
                    copyToClipboard(display, "Signature");
                  }}
                  style={{ fontSize: 11, height: 22, padding: "0 6px" }}
                >
                  Copy
                </Button>
              </div>
              <Card
                size="small"
                style={{
                  background: darkMode ? "#1f1f1f" : "#fafafa",
                  borderRadius: 4,
                  fontFamily: "monospace",
                  fontSize: 12,
                  border: `1px solid ${darkMode ? "#303030" : "#e8e8e8"}`,
                }}
              >
                {getSignatureDisplay(
                  item,
                  "signature" in item ? item.signature : null
                )}
              </Card>
            </div>
          )}

          {/* Module */}
          <div style={{ marginBottom: 16 }}>
            <Text strong style={{ fontSize: 12, color: darkMode ? "#8c8c8c" : "#666" }}>
              MODULE
            </Text>
            <div style={{ fontSize: 12, marginTop: 4, color: darkMode ? "#d9d9d9" : "#333" }}>
              {item.module}
            </div>
          </div>

          {/* Documentation */}
          {docContent.description || docContent.codeBlocks.length > 0 ? (
            <div>
              <Text strong style={{ fontSize: 12, color: darkMode ? "#8c8c8c" : "#666" }}>
                DOCUMENTATION
              </Text>
              <div
                style={{
                  marginTop: 12,
                  paddingTop: 12,
                  borderTop: `1px solid ${darkMode ? "#303030" : "#f0f0f0"}`,
                }}
              >
                {/* Render description text */}
                {docContent.description && (
                  <Paragraph
                    style={{
                      margin: docContent.codeBlocks.length > 0 ? "0 0 20px 0" : 0,
                      whiteSpace: "pre-wrap",
                      fontSize: 13,
                      lineHeight: 1.6,
                      color: darkMode ? "#d9d9d9" : "#333",
                    }}
                  >
                    {docContent.description}
                  </Paragraph>
                )}
                
                {/* Render code blocks */}
                {docContent.codeBlocks.map((block, index) => (
                  <div key={index} style={{ marginBottom: 20, position: "relative" }}>
                    <div style={{ 
                      display: "flex", 
                      justifyContent: "space-between", 
                      alignItems: "center",
                      marginBottom: 8 
                    }}>
                      <Tag 
                        color={darkMode ? "blue" : "geekblue"}
                        style={{ fontSize: 10, fontWeight: 500 }}
                      >
                        {block.language.toUpperCase()}
                      </Tag>
                      <Button
                        size="small"
                        type="text"
                        icon={<CopyOutlined />}
                        onClick={() => copyToClipboard(block.code, "code sample")}
                        style={{ 
                          fontSize: 11,
                          height: 22,
                          padding: "0 6px"
                        }}
                      >
                        Copy Code
                      </Button>
                    </div>
                    <SyntaxHighlighter
                      language={block.language}
                      style={darkMode ? vscDarkPlus : vs}
                      customStyle={{
                        margin: 0,
                        borderRadius: 4,
                        fontSize: 12,
                        lineHeight: 1.4,
                        background: darkMode ? "#1a1a1a" : "#f5f5f5",
                        border: `1px solid ${darkMode ? "#333" : "#e8e8e8"}`,
                      }}
                      showLineNumbers
                      wrapLongLines
                    >
                      {block.code}
                    </SyntaxHighlighter>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      </Modal>
    );
  };

  const folderStructure = useMemo(() => organizeModulesByFolder(searchResults.modules), [searchResults.modules]);

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
          {Object.keys(processedModules).length === 0 ? (
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
            <Collapse accordion ghost style={{ background: "transparent" }}>
              {renderFolderStructure(folderStructure)}
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