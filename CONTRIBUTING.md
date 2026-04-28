# Contributing to Data Analysis Multi-Agent System

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## 🌟 Ways to Contribute

- **Bug Reports**: Found a bug? Open an issue with detailed reproduction steps
- **Feature Requests**: Have an idea? Share it in the issues section
- **Code Contributions**: Submit pull requests for bug fixes or new features
- **Documentation**: Improve README, guides, or code comments
- **Testing**: Help test new features and report issues

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/data_analysis_agents.git
cd data_analysis_agents

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/data_analysis_agents.git
```

### 2. Set Up Development Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Configure your API keys in .env
# API_PROVIDER=siliconflow
# SILICONFLOW_API_KEY=your-key-here
```

### 3. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

## 📝 Development Guidelines

### Code Style

- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Add docstrings for classes and functions
- Keep functions focused and concise

Example:
```python
def execute_sql(sql: str, connection) -> dict:
    """
    Execute SQL query with safety checks.
    
    Args:
        sql: SQL query string
        connection: Database connection object
        
    Returns:
        dict: Query results with columns and rows
        
    Raises:
        ValueError: If SQL contains dangerous operations
    """
    # Implementation here
```

### Project Structure

- `core/` - Shared state definitions
- `agents/` - Agent implementations (Planner, Coder, Critic, Executor, Reporter)
- `tools/` - Database and external service integrations
- `workflow.py` - LangGraph orchestration logic
- `main.py` - Entry point for testing

### Adding New Agents

1. Define agent class in `agents/agents.py`:
```python
class NewAgent:
    SYSTEM_PROMPT = """Your agent's system prompt here"""
    
    def run(self, state: AnalysisState) -> AnalysisState:
        # Agent logic here
        return state
```

2. Register in `workflow.py`:
```python
workflow.add_node("new_agent", NewAgent().run)
workflow.add_edge("previous_node", "new_agent")
```

### Testing

Before submitting:

```bash
# Test API connection
python test_api.py

# Run main workflow
python main.py

# Test with real database (if configured)
USE_REAL_DB=true python main.py
```

## 🔍 Pull Request Process

### 1. Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Documentation updated (if needed)
- [ ] Commit messages are clear and descriptive
- [ ] No sensitive data (API keys, passwords) in commits

### 2. Commit Messages

Use clear, descriptive commit messages:

```bash
# Good
git commit -m "Add SQL validation in Critic agent"
git commit -m "Fix memory leak in database connection pool"
git commit -m "Update README with deployment instructions"

# Avoid
git commit -m "fix bug"
git commit -m "update"
```

### 3. Submit Pull Request

1. Push your branch to your fork:
```bash
git push origin feature/your-feature-name
```

2. Open a Pull Request on GitHub with:
   - Clear title describing the change
   - Detailed description of what and why
   - Reference related issues (e.g., "Fixes #123")
   - Screenshots/examples if applicable

### 4. Code Review

- Respond to feedback promptly
- Make requested changes in new commits
- Keep discussions focused and professional

## 🐛 Reporting Bugs

When reporting bugs, include:

1. **Environment**:
   - Python version
   - Operating system
   - API provider (SiliconFlow/Anthropic)
   - Database type (MySQL/Mock)

2. **Steps to Reproduce**:
   - Exact commands run
   - Input data/questions
   - Configuration settings

3. **Expected vs Actual Behavior**:
   - What should happen
   - What actually happened

4. **Logs/Error Messages**:
   - Full error traceback
   - Relevant console output

Example:
```
**Environment:**
- Python 3.10.5
- Windows 11
- SiliconFlow + DeepSeek V4
- MySQL 8.0

**Steps:**
1. Set USE_REAL_DB=true
2. Run python main.py
3. Ask: "分析销售趋势"

**Expected:** SQL executes successfully
**Actual:** Connection timeout error

**Error:**
pymysql.err.OperationalError: (2003, "Can't connect to MySQL server...")
```

## 💡 Feature Requests

When requesting features:

1. **Use Case**: Describe the problem you're trying to solve
2. **Proposed Solution**: How you envision it working
3. **Alternatives**: Other approaches you've considered
4. **Priority**: How important is this to you?

## 🔒 Security

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email the maintainer directly (if contact provided)
3. Include detailed description and reproduction steps
4. Allow time for a fix before public disclosure

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes (for significant contributions)
- README acknowledgments section

## 📞 Questions?

- Open a discussion on GitHub
- Check existing issues and documentation
- Review [NOTES.md](NOTES.md) for development tips

---

Thank you for contributing to make this project better! 🎉
