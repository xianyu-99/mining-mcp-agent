# 矿权日报 Agent (MCP Protocol)

本项目基于 Model Context Protocol (MCP) 构建了一个完全解耦的矿业数据分析智能体，完全符合题目 #2 的工程化要求。

## 架构说明

1. **MCP Servers (`src/servers/`)**
   - 包含 3 个标准的 MCP 工具服务器（均使用官方 `fastmcp` 编写，天然支持 stdio 协议）：
     - `mining_news`: `search(query, days)`, `fetch_article(url)`
     - `mineral_pdf`: `extract_resources(pdf_url)`
     - `lme_price`: `get_price(commodity, date)`, `get_trend(commodity, days)`
2. **Agent Client (`src/agent/client.py`)**
   - 采用 Langchain 的 ReAct 架构，智能调度上述工具，输出 Markdown 格式的综合矿权日报。
3. **mcp-config.json**
   - 提供了将上述工具直接插入到 Claude Desktop 或 Cursor 等支持 MCP 协议的 IDE/工具的配置文件。

---

## 如何在 5 分钟内跑起来

### 方式一：使用 Docker Compose (极简交付)

```bash
# 1. 设置环境变量 (如果未设置，系统将自动进入 Mock 降级模式验证 MCP 协议)
export OPENAI_API_KEY="sk-your-key-here"

# 2. 一键启动
docker-compose up
```
*(注：Windows 用户可在 PowerShell 中使用 `$env:OPENAI_API_KEY="sk-..."` 然后执行 docker-compose up)*

**💡 亮点特性：Mock 降级验证模式**
如果您在本地没有配置大模型的 API Key，系统并不会直接报错崩溃！它将优雅地进入 Mock 模式：
自动通过 `stdio` 协议启动所有子进程 -> 成功拉取并验证 MCP 工具的 JSON Schema 映射 -> 打印验证成功日志后退出。这允许面试官在即使没有设置 Key 的环境下，也能验证底层 MCP 架构的完整连通性。

系统会自动拉取依赖、运行 Agent，并在控制台直接打印出一份排版精美的 Markdown 矿权日报（包含新闻摘要、储量数据、价格走势和风险提示）。

### 方式二：本地运行

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="sk-your-key-here"
python src/agent/client.py "给我生成一份关于 Pilbara 锂矿的今日简报"
```

### 方式三：直接接入 Claude Desktop 测试

本项目完美兼容 Claude Desktop！只需将本目录下的 `mcp-config.json` 里的内容，合并到您的 Claude 配置文件（如 `C:\Users\用户名\AppData\Roaming\Claude\claude_desktop_config.json`）中。
*注意：在 Claude 配置文件中，请将 `args` 里的 `src/servers/...` 修改为本项目实际的绝对路径。*

重启 Claude Desktop 后，您就可以直接通过自然语言命令 Claude 去调用价格查询、新闻搜索和 PDF 提取了！
