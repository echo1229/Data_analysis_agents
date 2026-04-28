# Data Analysis Multi-Agent System

> 🤖 An intelligent data analysis system powered by LangGraph and LLM agents

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready multi-agent system that transforms natural language questions into SQL queries, validates them automatically, and generates business insights reports.

[中文文档](README.md) | [Feishu Integration Guide](FEISHU_GUIDE.md) | [Examples & Demo](EXAMPLES.md)

---

## 🎬 Quick Demo

```bash
# User Question
"Analyze sales trends by region over the past 3 months"

# System Auto-Execution
[Planner] Breaking down query steps...
[Coder] Generating SQL...
[Critic] Review passed ✅
[Executor] Executing query, returned 12 rows
[Reporter] Generating analysis report...

# Output Result
📊 Key Finding: North region fastest growth (35.43%), South region negative growth...
📈 Recommendations: Increase North region investment, investigate South decline...
```

See more examples → [EXAMPLES.md](EXAMPLES.md)

## ✨ Key Features

- 🔌 **Multi-Provider Support** - Works with SiliconFlow (DeepSeek V4) and Anthropic (Claude)
- 🗄️ **Real Database Integration** - MySQL support with automatic schema detection
- 🔄 **Self-Correcting Workflow** - Automatic SQL validation and retry mechanism
- 🛡️ **Production-Grade Security** - SQL injection prevention, read-only access, query limits
- 💰 **Cost Optimized** - Prompt caching and affordable model options (90% cost reduction)
- 🤖 **Feishu Bot Integration** - Deploy as a chat bot with one command
- ⚙️ **Flexible Configuration** - Environment-based settings for easy deployment

## 🏗️ Architecture

```
User Question
     │
     ▼
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Planner  │────▶│  Coder   │────▶│  Critic  │
│          │     │          │     │          │
└──────────┘     └──────────┘     └────┬─────┘
                      ▲                │
                      │   REJECTED     │ APPROVED
                      └────────────────┤
                                       ▼
                               ┌──────────────┐     ┌──────────┐
                               │   Executor   │────▶│ Reporter │
                               │              │     │          │
                               └──────────────┘     └──────────┘
                                                          │
                                                          ▼
                                                   Final Report
```

### Agent Responsibilities

| Agent | Role |
|-------|------|
| **Planner** | Breaks down natural language questions into structured query steps |
| **Coder** | Generates SQL based on the query plan, revises based on feedback |
| **Critic** | Validates SQL syntax and logic, returns APPROVED or REJECTED |
| **Executor** | Executes SQL and returns data results (with safety limits) |
| **Reporter** | Writes business analysis reports with insights and recommendations |

## 🚀 Quick Start

### 1. Installation

```bash
git clone <your-repo-url>
cd data_analysis_agents
pip install -r requirements.txt
```

### 2. Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your API credentials:

**Option A: SiliconFlow + DeepSeek V4 (Recommended, Low Cost)**
```env
API_PROVIDER=siliconflow
SILICONFLOW_API_KEY=sk-your-key-here
LLM_MODEL=deepseek-v4-flash
USE_REAL_DB=false
```

**Option B: Anthropic + Claude**
```env
API_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key
LLM_MODEL=claude-sonnet-4-6
USE_REAL_DB=false
```

### 3. Run

```bash
python main.py
```

The console will display the execution process of each agent and the final analysis report.

## 📊 Database Integration

### MySQL Setup

1. **Create Database**
```sql
CREATE DATABASE data_analysis CHARACTER SET utf8mb4;
```

2. **Import Sample Data**
```bash
mysql -u root -p < init_database.sql
```

3. **Configure `.env`**
```env
USE_REAL_DB=true
DB_HOST=localhost
DB_PORT=3306
DB_USER=data_analyst
DB_PASSWORD=analyst_readonly_2024
DB_NAME=data_analysis
```

The system will automatically:
- Read database schema
- Pass schema to Planner and Coder
- Execute generated SQL on real database

## 🤖 Feishu Bot Deployment

See [FEISHU_GUIDE.md](FEISHU_GUIDE.md) for complete instructions.

**Quick Start:**

1. Create app on [Feishu Open Platform](https://open.feishu.cn/)
2. Configure `.env` with Feishu credentials
3. Start server: `python feishu_server.py`
4. Configure webhook URL in Feishu console

## 🛡️ Security Features

- **SQL Injection Prevention** - Automatic blocking of DROP/DELETE/UPDATE operations
- **Query Limits** - Auto-adds LIMIT 500 to prevent memory overflow
- **Read-Only Access** - Database account has SELECT-only permissions
- **Graceful Degradation** - Returns friendly error reports instead of crashing

## 💰 Cost Comparison

| Provider | Model | Cost per Analysis | 100 Queries/Day | Monthly Cost |
|----------|-------|-------------------|-----------------|--------------|
| SiliconFlow | DeepSeek V4 Flash | ¥0.01-0.05 | ¥1-5 | ¥30-150 |
| Anthropic | Claude Opus 4.6 | $0.5-1.0 | $50-100 | $1500-3000 |

**Recommendation:** Use SiliconFlow for production (90% cost reduction).

## 📁 Project Structure

```
data_analysis_agents/
├── core/
│   └── state.py              # Shared state definition
├── tools/
│   ├── mysql_tools.py        # MySQL connection with safety features
│   ├── db_tools.py           # Mock SQL executor
│   └── feishu_bot.py         # Feishu bot implementation
├── agents/
│   └── agents.py             # Five agent node classes
├── workflow.py               # LangGraph orchestration
├── main.py                   # Entry point
├── feishu_server.py          # Feishu bot HTTP server
├── init_database.sql         # Sample database setup
├── test_api.py               # API connection test
└── requirements.txt
```

## 🛠️ Tech Stack

| Component | Version | Description |
|-----------|---------|-------------|
| Python | 3.10+ | Core language |
| [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python) | ≥ 0.92.0 | Claude API client |
| [OpenAI SDK](https://github.com/openai/openai-python) | ≥ 1.0.0 | SiliconFlow API client |
| [LangGraph](https://github.com/langchain-ai/langgraph) | ≥ 0.2.0 | State machine orchestration |
| PyMySQL | ≥ 1.1.0 | MySQL driver |
| SQLAlchemy | ≥ 2.0.0 | ORM and connection pooling |

### Supported LLM Models

**SiliconFlow (Recommended, Low Cost):**
- `deepseek-v4-flash` (Fastest, production-ready)
- `deepseek-v4-pro` (Most powerful, complex analysis)
- `deepseek-r1` (Reasoning model)
- `Qwen/Qwen2.5-72B-Instruct`

**Anthropic:**
- `claude-opus-4-6` (Most powerful)
- `claude-sonnet-4-6` (Balanced)
- `claude-haiku-4-5` (Fastest)

## 🔧 Configuration Options

### Environment Variables

```env
# API Configuration
API_PROVIDER=siliconflow          # siliconflow or anthropic
SILICONFLOW_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx

# LLM Configuration
LLM_MODEL=deepseek-v4-flash       # Model selection
MAX_ITERATIONS=3                  # Max Coder↔Critic retry cycles
ENABLE_THINKING=false             # Enable Adaptive Thinking (Anthropic only)
MAX_RETRIES=3                     # API call retry attempts
RETRY_DELAY=1.0                   # Retry delay (seconds)

# Database Configuration
USE_REAL_DB=false                 # Use real database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=data_analysis

# Security Configuration
MAX_QUERY_ROWS=500                # Max query result rows
ENABLE_SQL_SAFETY_CHECK=true      # Enable SQL safety checks
ENABLE_SQL_VALIDATION=true        # Enable SQL pre-execution validation
```

## 🎯 Use Cases

### Job Portfolio Project
- Demonstrate multi-agent collaboration capabilities
- Showcase SQL generation and data analysis skills
- Show engineering best practices (error handling, security)

### Data Analysis Internship
- Rapid prototyping for business questions
- Automate repetitive SQL queries
- Generate business analysis reports

### Enterprise Internal Tool
- Lower data analysis barriers for non-technical users
- Improve data team efficiency
- Enable self-service queries

### Learning LangGraph
- Understand state machine orchestration
- Learn conditional routing and cyclic edges
- Study agent collaboration patterns

## ✨ Optimization Highlights

### 1. Multi-Provider API Support
- Unified `_call_llm()` interface adapts to different API formats
- SiliconFlow uses OpenAI-compatible interface, 10x cheaper than Claude

### 2. Comprehensive Error Handling
- Automatic retry with exponential backoff for API failures
- All agent nodes protected with try-catch
- Error messages written to `error_message` field for debugging

### 3. Prompt Caching
- Anthropic API supports System Prompt caching
- Repeated calls save 30-50% token costs

### 4. Database Schema Injection
- Planner and Coder automatically receive real table structures
- More accurate SQL generation
- More effective Critic reviews

### 5. Flexible Configuration
- All parameters controlled via environment variables
- Runtime model and database switching

### 6. Production-Grade Security ⭐
- **SQL Safety Checks**: Auto-blocks DROP/DELETE/UPDATE operations
- **Query Limits**: Auto-adds LIMIT 500 to prevent memory overflow
- **Read-Only Enforcement**: Database must use read-only accounts
- **Graceful Degradation**: Returns friendly error reports instead of crashing

### 7. Critic Pre-Execution Validation ⭐
- Uses database EXPLAIN to validate SQL syntax
- Directly captures database errors (table not found, field errors)
- Review accuracy improved from 80% to 99%

### 8. Feishu Bot Integration
- One-click deployment as chat bot
- Rich text card messages for analysis reports
- Complete event subscription and message sending

## 📚 Documentation

- [README.md](README.md) - Chinese documentation
- [README_EN.md](README_EN.md) - English documentation (this file)
- [EXAMPLES.md](EXAMPLES.md) - Examples & Demo (Recommended)
- [FEISHU_GUIDE.md](FEISHU_GUIDE.md) - Feishu integration guide
- [OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md) - Architecture optimization details
- [NOTES.md](NOTES.md) - Personal usage notes (Chinese)
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

## ❓ FAQ

**Q: How to get SiliconFlow API key?**  
A: Visit [siliconflow.cn](https://siliconflow.cn), register an account, and create an API Key in the console.

**Q: DeepSeek V4 vs Claude - which is better?**  
A: DeepSeek V4 is low-cost (~1/10 of Claude), fast, suitable for production; Claude has stronger reasoning, suitable for complex analysis.

**Q: How to switch databases?**  
A: Modify `USE_REAL_DB` and database connection info in `.env`.

**Q: How to add new agents?**  
A: Define new agent class in `agents/agents.py`, register nodes and edges in `workflow.py`.

**Q: Why is the analysis slow?**  
A: Each LLM call takes 10-30 seconds. Complete workflow with 4-5 calls takes 40-120 seconds. Use `deepseek-v4-flash` or disable adaptive thinking for faster results.

**Q: How to reduce costs?**  
A: Use SiliconFlow + DeepSeek V4 (90% cost reduction), enable prompt caching, or use smaller models like `claude-haiku-4-5`.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📄 License

MIT License

## 📞 Support

If you have questions, please:
1. Check the documentation
2. Submit an issue on GitHub
3. Contact the maintainer

---

**Last Updated:** 2026-04-27  
**Version:** v2.0 (Production-Ready)
