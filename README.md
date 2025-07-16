# Pandora: Autonomous AI Agent Framework

![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Pandora is an advanced, extensible AI agent framework for orchestrating and executing complex, multi-step tasks. Built for robust reasoning, dynamic planning, and integrated tool usage, Pandora offers a solid foundation for intelligent assistant applications, automation, and research projects.

---

## 🚀 Features

- **Autonomous Reasoning**: Breaks down complex problems into actionable steps and iteratively executes them.
- **LLM Integration**: Supports state-of-the-art models (OpenAI GPT family, Google Gemini, and more).
- **Tool-Augmented Execution**: Provides tools for communication, file I/O, web search, Bash commands, plan generation, and even code synthesis.
- **Error Handling & Feedback Loops**: Recovers from errors and adapts plans using status updates and verification strategies.
- **Extensible & Modular**: Easily add or customize tools, agent behaviors, or workflows.

---

## 🏗️ Architecture Overview

- **Entry Point**: The engine manages conversations, state, tool-calls, and reasoning cycles.
- **Key Modules**:
    - `engine.py`: Orchestrates LLM calls, user interaction, tool execution, and control flow.
    - `tools.py`: Implements all tool functions (file, web, bash, planning, codegen, etc.).
    - `definitions.py`: Schemas/metadata for available tools, used for function-calling and planning.
    - `system_config.py`: The Pandora "system prompt" defining its principles and operational philosophy.
    - `types.py`: Core dataclasses and enums for message roles, tool calls, etc.
    - `log.py`: Structured logging for debugging and traceability.
- **Extensible Tool System**: Tools are methods with structured argument passing and output, easily extended or swapped out.

---

## ⚡ Getting Started

### Prerequisites

- **Python 3.12+** (leverages modern typing and async features)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/pandora.git
   cd pandora
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -e .
   ```

### Configuration

Pandora requires API keys for at least one LLM backend (OpenAI, Gemini, etc.), and optionally for enabled tools like web search.

- **Create a `.env` file** in the project root:
  ```env
  OPENAI_API_KEY="sk-..."
  GEMINI_API_KEY="..."
  TAVILY_API_KEY="..."
  ```

---

## 🧑‍💻 Usage

Pandora runs from the CLI (main function referenced in pyproject.toml scripts as `pandora:main`).

```bash
pandora
```

You'll enter an interactive session where you can pose tasks/questions. The agent will automatically plan, select tools, run processes, and report results step-by-step.

---

## 🛠️ Available Tools (Out of the Box)

- `echo`: Print or display status/progress messages
- `read_file` / `write_file`: File system read/write access (with safety checks)
- `web_search`: Online, real-time AI-powered search using LLM models
- `execute_bash`: Shell command execution with full output/error capture
- `build_plan`: Given a task, generate a detailed execution plan
- `generate_code`: Structured code generation for a path/language, using LLMs

*Adding your own tools is as simple as writing an async method and updating the definitions/config.*

---

## 🧩 Project Structure

```
src/pandora/
    engine.py         # Main orchestration loop and async engine
    tools.py          # Tool definitions and async implementations
    definitions.py    # Tool schemas for structured execution
    system_config.py  # AI agent's system prompt and philosophy
    types.py          # Message, role, and enum dataclasses
    log.py            # Project-wide structured logging config
README.md
pyproject.toml
```

---

## 🧑‍🌾 Extending Pandora

- **Add New Tools**: Define a new async method in `ToolsHandler`, update the schema in `definitions.py`, and register in the handler.
- **Change Core Logic**: The engine, planning, and loop are all modular Python. Use provided types and patterns for consistency.
- **Model Backend**: Easily swap models or access methods—just supply the environment variable for key(s).

---

## 📝 License

MIT License. See `LICENSE` for details.

---

## 💡 Inspiration & Philosophy

Pandora is designed with reliability, transparency, reasoning, and proactive action in mind. Its agentic loop is suitable for research, automation, and building powerful task assistants.

---

## 🤝 Contributing

Contributions are welcome! Please open issues or PRs for improvements, extensions, or questions.
