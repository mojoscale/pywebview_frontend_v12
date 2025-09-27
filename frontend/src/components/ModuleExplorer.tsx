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
} from "antd";
import {
  StarOutlined,
  StarFilled,
  FileSearchOutlined,
  MoonOutlined,
  SunOutlined,
  FunctionOutlined,
  CrownOutlined,
  CodeOutlined,
  ApiOutlined,
  SearchOutlined,
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
  const [favorites, setFavorites] = useState<Record<string, boolean>>({});
  const [darkMode, setDarkMode] = useState(false);
  const [activePanels, setActivePanels] = useState<string[]>([]);

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

  // Load favorites
  useEffect(() => {
    const saved = localStorage.getItem("moduleExplorerFavorites");
    if (saved) setFavorites(JSON.parse(saved));
  }, []);

  // Save favorites
  useEffect(() => {
    localStorage.setItem("moduleExplorerFavorites", JSON.stringify(favorites));
  }, [favorites]);

  // Flatten for search
  const flattened: ExplorerItem[] = useMemo(() => {
    const list: ExplorerItem[] = [];
    Object.entries(rawModules).forEach(([modName, mod]) => {
      mod.functions?.forEach((fn) =>
        list.push({
          module: modName,
          type: "function",
          ...fn,
        })
      );
      mod.classes?.forEach((cls) => {
        list.push({
          module: modName,
          type: "class",
          ...cls,
        });
        cls.methods?.forEach((m) =>
          list.push({
            module: modName,
            type: "method",
            parentClass: cls.name,
            ...m,
          })
        );
      });
      mod.variables?.forEach((v) =>
        list.push({
          module: modName,
          type: "variable",
          ...v,
        })
      );
    });
    return list;
  }, [rawModules]);

  // Search with fuse
  const searchResults = useMemo(() => {
    if (!search.trim()) {
      return {
        modules: rawModules,
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
  }, [search, flattened, rawModules]);

  // Toggle favorites
  const toggleFavorite = (key: string) =>
    setFavorites((prev) => ({ ...prev, [key]: !prev[key] }));

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

  // Render entry card
  const renderEntry = (item: ExplorerItem) => {
    const key = `${item.module}.${item.type}.${
      "parentClass" in item ? item.parentClass : ""
    }.${item.name}`;
    const typeConfig = getTypeConfig(item.type);

    return (
      <Card
        size="small"
        hoverable
        style={{
          marginBottom: 8,
          border: `1px solid ${darkMode ? "#434343" : "#f0f0f0"}`,
          borderRadius: 6,
          background: darkMode ? "rgba(255,255,255,0.02)" : "#fff",
        }}
        bodyStyle={{ padding: 12 }}
        title={
          <Space style={{ width: "100%", justifyContent: "space-between" }}>
            <Space>
              <Avatar
                size="small"
                icon={typeConfig.icon}
                style={{
                  backgroundColor: typeConfig.color,
                  fontSize: 12,
                }}
              />
              <Text
                strong
                style={{ color: darkMode ? "#fff" : "#000", fontSize: 13 }}
              >
                {item.type === "method"
                  ? `${(item as any).parentClass}.${item.name}`
                  : item.name}
              </Text>
              {"signature" in item && item.signature && (
                <Tag
                  color={darkMode ? "blue" : "geekblue"}
                  style={{ margin: 0, fontSize: 10 }}
                >
                  {item.signature}
                </Tag>
              )}
            </Space>
            <Button
              type="text"
              size="small"
              icon={
                favorites[key] ? (
                  <StarFilled style={{ color: "#faad14" }} />
                ) : (
                  <StarOutlined
                    style={{ color: darkMode ? "#8c8c8c" : "#d9d9d9" }}
                  />
                )
              }
              onClick={(e) => {
                e.stopPropagation();
                toggleFavorite(key);
              }}
            />
          </Space>
        }
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {"doc" in item && item.doc && (
            <Paragraph
              type="secondary"
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
          {"value" in item && item.value && (
            <Tag
              color={darkMode ? "blue" : "cyan"}
              style={{ margin: 0, alignSelf: "flex-start", fontSize: 10 }}
            >
              {item.value}
            </Tag>
          )}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Tag
              style={{
                fontSize: 9,
                padding: "1px 6px",
                border: `1px solid ${typeConfig.color}20`,
                color: typeConfig.color,
                background: `${typeConfig.color}10`,
              }}
            >
              {typeConfig.label}
            </Tag>
            <Text type="secondary" style={{ fontSize: 10 }}>
              {item.module}
            </Text>
          </div>
        </div>
      </Card>
    );
  };

  const favoriteCount = Object.values(favorites).filter(Boolean).length;
  const displayModules = searchResults.hasSearch
    ? searchResults.modules
    : rawModules;

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
            count={Object.keys(rawModules).length}
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
          placeholder="Search functions, classes, variables..."
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
        <Tabs
          defaultActiveKey="all"
          size="small"
          style={{ height: "100%" }}
          items={[
            {
              key: "all",
              label: (
                <Space>
                  <CodeOutlined />
                  All Modules
                  {searchResults.hasSearch && (
                    <Badge
                      count={Object.keys(displayModules).length}
                      size="small"
                    />
                  )}
                </Space>
              ),
              children: (
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
                          : [
                              ...(mod.functions || []).map(
                                (f: FunctionEntry) => ({
                                  ...f,
                                  type: "function" as const,
                                  module: modName,
                                })
                              ),
                              ...(mod.classes || []).map((c: ClassEntry) => ({
                                ...c,
                                type: "class" as const,
                                module: modName,
                              })),
                              ...(mod.variables || []).map(
                                (v: VariableEntry) => ({
                                  ...v,
                                  type: "variable" as const,
                                  module: modName,
                                })
                              ),
                            ];

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
              ),
            },
            {
              key: "favorites",
              label: (
                <Space>
                  <StarFilled style={{ color: "#faad14" }} />
                  Favorites
                  <Badge count={favoriteCount} size="small" color="gold" />
                </Space>
              ),
              children: (
                <div style={{ padding: "0 16px 16px 16px" }}>
                  <List
                    dataSource={flattened.filter(
                      (f) =>
                        favorites[
                          `${f.module}.${f.type}.${
                            "parentClass" in f ? f.parentClass : ""
                          }.${f.name}`
                        ]
                    )}
                    renderItem={(item: ExplorerItem) => (
                      <List.Item style={{ padding: "4px 0" }}>
                        {renderEntry(item)}
                      </List.Item>
                    )}
                    locale={{
                      emptyText: (
                        <Empty
                          image={Empty.PRESENTED_IMAGE_SIMPLE}
                          description="No favorites yet"
                          style={{ margin: "40px 0" }}
                        >
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            Click the star icon on any item to add it to
                            favorites
                          </Text>
                        </Empty>
                      ),
                    }}
                  />
                </div>
              ),
            },
          ]}
          tabBarStyle={{
            background: darkMode ? "#141414" : "#fafafa",
            padding: "0 16px",
            marginBottom: 0,
          }}
        />
      </div>
    </div>
  );
};

export default ModuleExplorer;
