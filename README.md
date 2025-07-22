# Pandora: Universal Agent Framework

![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![UV](https://img.shields.io/badge/uv-managed-blue.svg)](https://github.com/astral-sh/uv)

Pandora is an advanced autonomous AI agent framework implementing an agent loop with  ** Finite State Machine** for orchestrating complex multi-step tasks through structured reasoning and tool execution. Built with mathematical rigor and extensible architecture, Pandora provides a foundation for intelligent agent systems that can plan, execute, and adapt autonomously.

---

## 🧮 The finite state machine Algorithm

Pandora implements a novel approach to agent control flow through the **finite state machine*, which models agent behavior as a discrete action space with deterministic state transitions:

### Mathematical Foundation

- **State Space**: `S = {s₁, s₂, ..., sₙ}` where each `sᵢ` represents agent execution state
- **Core Action Space**: `Ω_core = {print_message, read_file, create_file, edit_file, search_web, execute_bash, generate_plan, apply_regex}`
- **Extended Action Space**: `Ω = Ω_core ∪ Ω_mcp` (MCP server integration)

### Trajectory Structure

Every agent trajectory `T` follows a **"sandwich" pattern**:
```
print_message → [action sequence] → print_message
```

### Control Flow Mapping

The FSM algorithm uses a control function `M: MessageType → {0, 1}`:
- **Interactive Mode** (`M = 0`): `{reply, ask, confirm}` → await user input
- **Autonomous Mode** (`M = 1`): `{think, update, notify, analyze}` → continue execution

### Key Invariants
1. **Trajectory Bookending**: Every trajectory begins and ends with `print_message`
2. **Deterministic Termination**: Agent cannot end without explicit terminating message
3. **State Consistency**: Mode transitions only occur through `print_message` calls
4. **Parallel Execution**: Independent tools can execute concurrently within constraints

---

## 🚀 Features

### Core Capabilities
- **Autonomous Reasoning**: Multi-step problem decomposition and execution
- **Tool-Augmented Intelligence**: Integrated file I/O, web search, bash execution, and code generation
- **MCP Integration**: Extensible through Model Context Protocol servers
- **Parallel Execution**: Concurrent tool calls for optimal performance
- **Advanced Planning**: O3/O3-mini/O4-mini reasoning models for complex task planning

### Tool Ecosystem
- **File Operations**: Read, create, edit files with LLM-powered modifications
- **Web Intelligence**: Real-time web search with contextual integration  
- **System Integration**: Bash command execution with full I/O capture
- **Pattern Matching**: Regex-based file transformations
- **Plan Generation**: Strategic task breakdown using advanced reasoning models
- **Message Control**: Structured communication with execution flow control

---

## ⚡ Quick Start

### Prerequisites
- **Python 3.12+** (async/await, modern typing)
- **UV Package Manager** (recommended) or pip

### Installation

Using UV (recommended):
```bash
git clone https://github.com/milkymap/pandora.git
cd pandora
uv sync
```

Using pip:
```bash
git clone https://github.com/milkymap/pandora.git
cd pandora
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Configuration

Create `.env` file with required API keys:
```env
OPENAI_API_KEY=sk-your-openai-key-here
# Optional: Add other service keys as needed
```

---

## 🎯 Usage

### Basic Execution
```bash
pandora --model gpt-4.1 --openai_api_key $OPENAI_API_KEY
```

### Advanced Options
```bash
pandora \
  --model gpt-4.1-mini \
  --openai_api_key $OPENAI_API_KEY \
  --path2mcp_servers_file config/mcp-servers.json \
  --startup_timeout 15.0 \
  --parallel_tool_calls
```

### Interactive Session Example
```
Enter a query: Create a Python script that analyzes CSV data and generates visualizations

[Agent follows UV algorithm:]
1. print_message(type="think") → enters autonomous mode
2. generate_plan() → creates execution strategy  
3. create_file() → writes analysis script
4. execute_bash() → tests the script
5. print_message(type="reply") → returns to interactive mode
```

---

## 🏗️ Architecture

### Core Components

```
src/pandora/
├── __init__.py           # CLI entry point and main loop
├── engine.py            # UV algorithm implementation and orchestration
├── definitions.py       # Tool schemas and metadata
├── system_config.py     # Mathematical system prompt and constraints  
├── mcp_servers_handler.py # MCP protocol integration
├── types.py            # Core data structures and enums
└── log.py              # Structured logging system
```

### MCP Integration

Pandora supports Model Context Protocol for extensible tool integration:
```json
{
  "servers": {
    "filesystem": {
      "command": "uvx",
      "args": ["mcp-server-filesystem", "/path/to/allowed/files"]
    }
  }
}
```

---

## 🛠️ Available Tools

| Tool | Description | Usage |
|------|-------------|-------|
| `print_message` | Control execution flow and communicate | State transitions, user interaction |
| `read_file` | Read file contents | Data analysis, code review |
| `create_file` | Create/overwrite files | Code generation, documentation |
| `edit_file` | LLM-powered file modifications | Intelligent code editing |
| `search_through_web` | Real-time web search | Research, current information |
| `execute_bash` | Shell command execution | Testing, system operations |
| `generate_plan` | Strategic task planning | Complex project breakdown |
| `apply_regex` | Pattern-based transformations | Bulk text processing |

---

## 🧪 Extension Guide

### Adding Custom Tools

1. **Define the tool function**:
```python
async def my_custom_tool(self, param1: str, param2: int) -> str:
    # Implementation
    return "Tool result"
```

2. **Add tool schema**:
```python
MY_CUSTOM_TOOL = {
    "type": "function",
    "function": {
        "name": "my_custom_tool",
        "description": "Tool description",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string"},
                "param2": {"type": "integer"}
            },
            "required": ["param1", "param2"]
        }
    }
}
```

3. **Register in engine**:
```python
# Add to tools list in engine.py
tools = [PRINT_MESSAGE, ..., MY_CUSTOM_TOOL]
```

### MCP Server Integration

Extend functionality through MCP servers without modifying core code:
```bash
uvx mcp-server-your-tool --config config.json
```

---

## 📊 Performance & Optimization

### Parallel Execution
Enable concurrent tool calls for independent operations:
```bash
pandora --parallel_tool_calls
```

### Model Selection
- **gpt-4.1**: Complex reasoning, code generation, comprehensive analysis
- **gpt-4.1-mini**: Fast execution, simple tasks, cost optimization
- **o3/o3-mini/o4-mini**: Advanced planning, complex problem decomposition

---

## 🔍 Debugging & Monitoring

### Structured Logging
Pandora provides comprehensive logging for trajectory analysis:
```python
from pandora.log import logger
logger.info("Agent state transition", extra={"state": "autonomous"})
```

### Execution Traces
Monitor agent behavior through tool call logging and state transitions.

---

## 📚 Research & Theory

Pandora implements concepts from:
- **Agent-based Systems**: Autonomous decision making and task execution
- **Formal Methods**: Mathematical constraints and invariants
- **Control Theory**: State machines and deterministic transitions
- **Distributed Systems**: Parallel execution and coordination

---

## 🤝 Contributing

We welcome contributions! Areas of interest:
- New tool implementations
- MCP server integrations  
- Performance optimizations
- Mathematical model refinements
- Documentation improvements

### Development Setup
```bash
git clone https://github.com/milkymap/pandora.git
cd pandora
uv sync --dev
uv run pytest tests/
```

---

## 📄 License

MIT License - see `LICENSE` file for details.

---

## 🙏 Acknowledgments

- **UV Package Manager** by Astral for modern Python dependency management
- **OpenAI** for LLM capabilities and function calling
- **Model Context Protocol** community for extensible tool integration
- **Python AsyncIO** ecosystem for high-performance concurrent execution

---

**Pandora** - *Where AI agents think, plan, and execute with mathematical precision.*