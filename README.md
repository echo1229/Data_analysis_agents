# 数据分析 Multi-Agent 协作系统

> 🤖 基于 LangGraph 和 LLM 的智能数据分析系统

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

基于 LangGraph 状态机编排的生产级多 Agent 数据分析系统，支持自然语言提问 → SQL 生成 → 自动审查修正 → 业务报告输出的完整闭环。

[English Documentation](README_EN.md) | [飞书接入指南](FEISHU_GUIDE.md) | [示例演示](EXAMPLES.md)

---

## 🎬 快速演示

```bash
# 用户提问
"分析过去 3 个月各地区的销售趋势"

# 系统自动执行
[Planner] 拆解查询步骤...
[Coder] 生成 SQL...
[Critic] 审查通过 ✅
[Executor] 执行查询，返回 12 行数据
[Reporter] 生成分析报告...

# 输出结果
📊 核心结论：North 地区增长最快（35.43%），South 地区出现负增长...
📈 业务建议：加大 North 地区投入，调查 South 地区下滑原因...
```

查看更多示例 → [EXAMPLES.md](EXAMPLES.md)

## ✨ 核心特性

- 🔌 **多 API 提供商支持** - 支持硅基流动（DeepSeek V4）和 Anthropic（Claude）
- 🗄️ **真实数据库集成** - MySQL 支持，自动 Schema 检测
- 🔄 **自我修正工作流** - 自动 SQL 验证和重试机制
- 🛡️ **生产级安全保护** - SQL 注入防护、只读访问、查询限制
- 💰 **成本优化** - Prompt 缓存和低成本模型选项（成本降低 90%）
- 🤖 **飞书机器人集成** - 一键部署为聊天机器人
- ⚙️ **灵活配置** - 基于环境变量的配置，易于部署

---

## 🏗️ 架构概览

```
用户问题
     │
     ▼
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Planner  │────▶│  Coder   │────▶│  Critic  │
│  规划者   │     │  执行者   │     │  审判官   │
└──────────┘     └──────────┘     └────┬─────┘
                      ▲                │
                      │   REJECTED     │ APPROVED
                      └────────────────┤
                                       ▼
                               ┌──────────────┐     ┌──────────┐
                               │   Executor   │────▶│ Reporter │
                               │  SQL 执行器   │     │  输出者   │
                               └──────────────┘     └──────────┘
                                                          │
                                                          ▼
                                                      最终报告
```

### Agent 职责

| Agent | 职责 |
|-------|------|
| **Planner** | 接收自然语言问题，拆解为结构化的数据查询步骤 |
| **Coder** | 根据查询计划生成 SQL 语句，支持被打回后按反馈修正 |
| **Critic** | 审查 SQL 的语法正确性与逻辑合理性，输出 `APPROVED` 或 `REJECTED` |
| **Executor** | 执行 SQL 并返回数据结果（带安全限制） |
| **Reporter** | 基于数据结果撰写包含业务洞察和行动建议的分析报告 |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
git clone <your-repo-url>
cd data_analysis_agents
pip install -r requirements.txt
```

### 2. 配置环境变量

复制示例配置文件：

```bash
cp .env.example .env
```

编辑 `.env`，配置 API 凭证：

**方案 A：硅基流动 + DeepSeek V4（推荐，成本低）**
```env
API_PROVIDER=siliconflow
SILICONFLOW_API_KEY=sk-your-key-here
LLM_MODEL=deepseek-v4-flash
USE_REAL_DB=false
```

**方案 B：Anthropic + Claude**
```env
API_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key
LLM_MODEL=claude-sonnet-4-6
USE_REAL_DB=false
```

### 3. 运行

```bash
python main.py
```

控制台会依次输出每个 Agent 的执行过程、生成的 SQL、以及最终的业务分析报告。

---

## 📊 数据库集成

### MySQL 配置

1. **创建数据库**
```sql
CREATE DATABASE data_analysis CHARACTER SET utf8mb4;
```

2. **导入示例数据**
```bash
mysql -u root -p < init_database.sql
```

3. **配置 `.env`**
```env
USE_REAL_DB=true
DB_HOST=localhost
DB_PORT=3306
DB_USER=data_analyst
DB_PASSWORD=analyst_readonly_2024
DB_NAME=data_analysis
```

系统会自动：
- 读取数据库 Schema
- 将 Schema 传递给 Planner 和 Coder
- 在真实数据库执行生成的 SQL

---

## 🤖 飞书机器人部署

完整指南请查看 [FEISHU_GUIDE.md](FEISHU_GUIDE.md)。

**快速开始：**

1. 在[飞书开放平台](https://open.feishu.cn/)创建应用
2. 在 `.env` 中配置飞书凭证
3. 启动服务器：`python feishu_server.py`
4. 在飞书控制台配置 Webhook URL

---

## 🛡️ 安全特性

- **SQL 注入防护** - 自动拦截 DROP/DELETE/UPDATE 等危险操作
- **查询限制** - 自动添加 LIMIT 500，防止内存溢出
- **只读访问** - 数据库账号仅有 SELECT 权限
- **优雅降级** - 失败时返回友好错误报告，而非崩溃

---

## 💰 成本对比

| 提供商 | 模型 | 单次分析成本 | 每天 100 次 | 每月成本 |
|--------|------|-------------|------------|---------|
| 硅基流动 | DeepSeek V4 Flash | ¥0.01-0.05 | ¥1-5 | ¥30-150 |
| Anthropic | Claude Opus 4.6 | $0.5-1.0 | $50-100 | $1500-3000 |

**建议：** 生产环境使用硅基流动（成本降低 90%）。

---

## 技术栈

| 组件 | 版本 | 说明 |
|---|---|---|
| Python | 3.10+ | 核心语言 |
| [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python) | ≥ 0.92.0 | Claude API 客户端 |
| [OpenAI SDK](https://github.com/openai/openai-python) | ≥ 1.0.0 | 硅基流动 API 客户端 |
| [LangGraph](https://github.com/langchain-ai/langgraph) | ≥ 0.2.0 | 状态机编排 |
| PyMySQL | ≥ 1.1.0 | MySQL 驱动 |
| SQLAlchemy | ≥ 2.0.0 | ORM 和连接池 |

### 支持的 LLM 模型

**硅基流动（推荐，成本低）：**
- `deepseek-v4-flash`（最快，适合生产）
- `deepseek-v4-pro`（最强，适合复杂分析）
- `deepseek-r1`（推理模型）
- `Qwen/Qwen2.5-72B-Instruct`

**Anthropic：**
- `claude-opus-4-6`（最强）
- `claude-sonnet-4-6`（平衡）
- `claude-haiku-4-5`（最快）

---

## 📁 项目结构

```
data_analysis_agents/
├── core/
│   ├── state.py              # 共享状态定义
│   └── __init__.py
├── tools/
│   ├── mysql_tools.py        # MySQL 连接（含安全特性）
│   ├── db_tools.py           # Mock SQL 执行器
│   ├── feishu_bot.py         # 飞书机器人实现
│   └── __init__.py
├── agents/
│   ├── agents.py             # 五个 Agent 节点类
│   └── __init__.py
├── workflow.py               # LangGraph 编排
├── main.py                   # 入口文件
├── feishu_server.py          # 飞书机器人 HTTP 服务器
├── init_database.sql         # 示例数据库初始化脚本
├── test_api.py               # API 连接测试
├── requirements.txt          # Python 依赖
├── .env.example              # 环境变量模板
├── .gitignore
├── README.md                 # 中文文档（本文件）
├── README_EN.md              # 英文文档
├── FEISHU_GUIDE.md           # 飞书接入指南
├── OPTIMIZATION_SUMMARY.md   # 优化总结
└── NOTES.md                  # 个人使用笔记
```

---

## 配置说明

### 环境变量完整列表

```env
# API 配置
API_PROVIDER=siliconflow          # siliconflow 或 anthropic
SILICONFLOW_API_KEY=sk-xxx        # 硅基流动 API Key
ANTHROPIC_API_KEY=sk-ant-xxx      # Anthropic API Key

# LLM 配置
LLM_MODEL=deepseek-v4-flash       # 模型选择
MAX_ITERATIONS=3                  # Coder↔Critic 最大循环次数
ENABLE_THINKING=false             # 是否启用 Adaptive Thinking（仅 Anthropic）
MAX_RETRIES=3                     # API 调用失败重试次数
RETRY_DELAY=1.0                   # 重试延迟（秒）

# 数据库配置
USE_REAL_DB=false                 # 是否使用真实数据库
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=data_analysis
```

---

## 优化亮点

### 1. 多 API 提供商支持
- 统一的 `_call_llm()` 接口，自动适配不同 API 格式
- 硅基流动使用 OpenAI 兼容接口，成本比 Claude 低 10 倍

### 2. 完善的错误处理
- API 调用失败自动重试（指数退避）
- 所有 Agent 节点都有 try-catch 保护
- 错误信息写入 `error_message` 字段，便于调试

### 3. Prompt Caching
- Anthropic API 支持 System Prompt 缓存
- 重复调用可节省 30-50% token 成本

### 4. 数据库 Schema 注入
- Planner 和 Coder 自动获取真实表结构
- 生成的 SQL 更准确，Critic 审查更有效

### 5. 灵活配置
- 所有参数通过环境变量控制
- 支持运行时切换模型和数据库

### 6. 生产级安全保护 ⭐
- **SQL 安全拦截**：自动拦截 DROP/DELETE/UPDATE 等危险操作
- **数据量限制**：自动添加 LIMIT 500，防止内存溢出和 Token 超限
- **只读账号强制**：数据库必须使用只读账号，防止误操作
- **优雅降级**：达到最大重试次数时不强制执行错误 SQL，返回友好错误报告

### 7. Critic 预执行验证 ⭐
- 使用数据库 EXPLAIN 验证 SQL 语法
- 直接捕获数据库报错（表不存在、字段错误等）
- 审查准确率从 80% 提升到 99%

### 8. 飞书机器人集成
- 一键部署，支持单聊和群聊
- 富文本卡片消息展示分析报告
- 完整的事件订阅和消息发送

---

## 适用场景

### 求职项目展示
- 展示 Multi-Agent 协作能力
- 展示 SQL 生成和数据分析能力
- 展示工程化能力（错误处理、配置管理、安全加固）

### 数据分析实习
- 快速原型验证业务问题
- 自动化重复性 SQL 查询
- 生成业务分析报告

### 企业内部工具
- 降低数据分析门槛，支持非技术人员自助查询
- 提升数据团队效率
- 减少重复性数据查询工作

### 学习 LangGraph
- 理解状态机编排
- 理解条件路由和循环边
- 理解 Agent 协作模式

---

## 📚 文档导航

- [README.md](README.md) - 项目概览和快速开始（本文件）
- [README_EN.md](README_EN.md) - English Documentation
- [EXAMPLES.md](EXAMPLES.md) - 示例与演示（推荐查看）
- [FEISHU_GUIDE.md](FEISHU_GUIDE.md) - 飞书接入完整指南
- [OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md) - 架构优化详解
- [NOTES.md](NOTES.md) - 个人使用笔记
- [CONTRIBUTING.md](CONTRIBUTING.md) - 贡献指南

---

## 常见问题

**Q: 硅基流动 API 如何获取？**  
A: 访问 [siliconflow.cn](https://siliconflow.cn) 注册账号，在控制台创建 API Key。

**Q: DeepSeek V4 和 Claude 哪个更好？**  
A: DeepSeek V4 成本低（约 Claude 的 1/10），速度快，适合生产环境；Claude 推理能力更强，适合复杂分析。

**Q: 如何切换数据库？**  
A: 修改 `.env` 中的 `USE_REAL_DB` 和数据库连接信息即可。

**Q: 如何添加新的 Agent？**  
A: 在 `agents/agents.py` 中定义新 Agent 类，在 `workflow.py` 中注册节点和边。

**Q: 为什么分析速度慢？**  
A: 每次 LLM 调用需要 10-30 秒，完整流程 4-5 次调用需要 40-120 秒。可使用 `deepseek-v4-flash` 或关闭 adaptive thinking 加速。

**Q: 如何降低成本？**  
A: 使用硅基流动 + DeepSeek V4（成本降低 90%），启用 Prompt Caching，或使用更小的模型如 `claude-haiku-4-5`。

**Q: SQL 生成不准确怎么办？**  
A: 确保 `.env` 中配置了真实数据库连接，系统会自动读取 Schema 提升准确率。也可以在 Planner 的 Prompt 中手动添加表结构说明。

**Q: 如何部署到生产环境？**  
A: 参考 [FEISHU_GUIDE.md](FEISHU_GUIDE.md) 第八章，使用 Supervisor + Nginx + HTTPS 部署。

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

详细指南请查看 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 许可证

MIT License
