Here's the complete updated README.md with all the latest changes, including the new `print_mode` parameter and other improvements:


# Pandora: Universal Agent Framework

![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![UV](https://img.shields.io/badge/uv-managed-blue.svg)](https://github.com/astral-sh/uv)

Pandora is an advanced autonomous AI agent framework implementing an agent loop with **Finite State Machine** for orchestrating complex multi-step tasks through structured reasoning and tool execution. Built with mathematical rigor and extensible architecture, Pandora provides a foundation for intelligent agent systems that can plan, execute, and adapt autonomously.

---

## 🧮 The Finite State Machine Algorithm

Pandora implements a novel approach to agent control flow through the **finite state machine**, which models agent behavior as a discrete action space with deterministic state transitions:

### Mathematical Foundation

- **State Space**: `S = {s₁, s₂, ..., sₙ}` where each `sᵢ` represents agent execution state
- **Core Action Space**: `Ω_core = {print_message, read_file, create_file, edit_file, search_web, execute_bash, generate_plan, apply_regex}`
- **Extended Action Space**: `Ω = Ω_core ∪ Ω_mcp` (MCP server integration)
- **Output Modes**: `M = {rich, json}` configurable display formats

### Enhanced Trajectory Structure

Every agent trajectory `T` follows a **"sandwich" pattern** with configurable output:
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
4. **Output Configurability**: Display format controlled via `print_mode` parameter
5. **Parallel Execution**: Independent tools can execute concurrently within constraints

---

## 🚀 Features

### Core Capabilities
- **Autonomous Reasoning**: Multi-step problem decomposition and execution
- **Tool-Augmented Intelligence**: Integrated file I/O, web search, bash execution, and code generation
- **MCP Integration**: Extensible through Model Context Protocol servers
- **Parallel Execution**: Concurrent tool calls for optimal performance
- **Advanced Planning**: O3/O3-mini/O4-mini reasoning models for complex task planning

### Enhanced Output System
- **Rich Mode**: Color-coded panels with message type indicators
- **JSON Mode**: Raw JSON output for programmatic processing
- **Dynamic Formatting**: Per-message display control
- **Visual Hierarchy**: Clear distinction between message types

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
  --parallel_tool_calls \
  --print_mode rich  # or 'json' for raw output
```

### Output Mode Examples

**Rich Mode (default):**
```bash
pandora --print_mode rich
```
Displays:
```
┌──────────────────────────────────────────────────┐
│  THINK: Analyzing task requirements             │
│                                                │
│  I'll need to:                                 │
│  1. Create project structure                   │
│  2. Implement core functionality               │
│  3. Add validation checks                      │
└──────────────────────────────────────────────────┘
```

**JSON Mode:**
```bash
pandora --print_mode json
```
Returns:
```json
{
  "message": "Analyzing task requirements...",
  "message_type": "think",
  "agent_loop_state": "autonomous"
}
```

### Interactive Session Example
```
Enter a query: Create a data analysis pipeline

[Agent follows UV algorithm with rich output:]
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
├── engine.py            # UV algorithm implementation
├── tools.py             # All tool implementations
├── definitions.py       # Tool schemas and metadata
├── system_config.py     # Mathematical system prompts  
├── mcp_servers_handler.py # MCP protocol integration
├── types.py            # Core data structures
└── log.py              # Structured logging
```

### Enhanced Output System
- **Rich Formatting**: Uses `rich` library for beautiful terminal output
- **Message Typing**: Color-coded by message type (think, reply, etc.)
- **Dynamic Control**: Switch between modes per-message or globally

---

## 🛠️ Available Tools

| Tool | Description | Output Control |
|------|-------------|----------------|
| `print_message` | Control flow with configurable output | rich/json modes |
| `read_file` | Read file contents | - |
| `create_file` | Create/overwrite files | - |
| `edit_file` | LLM-powered file edits | - |
| `search_through_web` | Web search with context | - |
| `execute_bash` | Shell command execution | - |
| `generate_plan` | Task planning | - |
| `apply_regex` | Pattern transformations | - |

---

## 📊 Output Formatting Guide

### Message Types and Styles

| Type | Color | Usage |
|------|-------|-------|
| `think` | Blue | Internal reasoning |
| `ask` | Yellow | User queries |
| `confirm` | Magenta | Confirmations |
| `analyze` | Cyan | Data analysis |
| `notify` | Green | Information |
| `update` | White | Progress updates |
| `reply` | Bold | Final responses |

### Customizing Output

1. **Global Default**:
   ```bash
   pandora --print_mode json
   ```

2. **Per-Message Control**:
   ```python
   await print_message(
       message="Analyzing data",
       message_type="think",
       print_mode="rich"  # Overrides global default
   )
   ```

---

## 🧪 Extension Guide

### Adding Custom Tools

1. **Define the tool** in `tools.py`:
```python
async def custom_tool(self, params) -> str:
    # Implementation
    return "Result"
```

2. **Add schema** in `definitions.py`:
```python
CUSTOM_TOOL = {
    "type": "function",
    "function": {
        "name": "custom_tool",
        "description": "...",
        "parameters": {...}
    }
}
```

3. **Register in engine**:
```python
tools = [PRINT_MESSAGE, ..., CUSTOM_TOOL]
```

### Creating New Output Formats

1. Extend `ToolExecutor.print_message()`
2. Add new format options
3. Update CLI argument choices

---

## 📚 Research & Theory

Pandora implements concepts from:
- **Agent-based Systems**: Autonomous decision making
- **Formal Methods**: Mathematical constraints
- **Control Theory**: State machines
- **Human-Computer Interaction**: Configurable outputs
- **Type Theory**: Structured message typing

---

## 🤝 Contributing

We welcome contributions! Areas of interest:
- New output formatters
- Enhanced rich display features
- Additional tool integrations
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

**Pandora** - *Where AI agents think, plan, and execute with mathematical precision and beautiful communication.*
```
