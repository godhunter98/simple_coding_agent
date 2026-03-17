# Simple Coding Agent

A lightweight CLI coding assistant that uses LLMs to help with common coding tasks.

## Features

- Read, list, and edit files through conversation
- Run bash commands and existing bash scripts
- 5 integrated tools
- Provider-agnostic LLM access via [litellm](https://github.com/BerriAI/litellm)
- Works with many models (OpenAI, Anthropic, Gemini, DeepSeek, local)
- Color-coded interactive CLI
- `.env` based configuration
- Warnings for risky shell operations

## Installation

### Prerequisites
- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Using uv (recommended)

```bash
# Clone the repository
git clone <repository-url>
cd simple-coding-agent

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows
```

### Using pip

```bash
# Clone the repository
git clone <repository-url>
cd simple-coding-agent

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows

# Install dependencies
pip install -e .
```

## Configuration

Create a `.env` file with at least:

```env
MODEL="deepseek/deepseek-coder"
API_KEY="your-api-key-here"
```

Optional settings:

```env
API_BASE="http://localhost:8000/v1"
USE_UV=1
```

### Supported models
Any model supported by litellm works.

## Usage

### Starting the agent

```bash
# Using uv
uv run python basic_coding_agent.py

# Using pip
python basic_coding_agent.py
```

### Basic commands

Example:

```
You: Can you read the main.py file?
Assistant: I'll read that file for you.
```

### Available tools

- `read_file(filename)`
- `list_file(path)`
- `edit_file(path, old_str, new_str)`
- `run_bash_command(command)`
- `run_existing_bash_script(script_path)`

#### Security note
Shell commands run with your permissions. Use caution and prefer file tools when possible.

### Exiting
Type `exit`, `quit`, or press `Ctrl+C`.

## Project structure

```
simple-coding-agent/
├── basic_coding_agent.py
├── main.py
├── README.md
├── pyproject.toml
├── uv.lock
├── .env
├── .env.example
├── .gitignore
├── .python-version
└── bug_fixes_summary.txt
```

## Development

### Dependencies
- `litellm`
- `python-dotenv`

### Adding new tools

1. Add a tool function in `basic_coding_agent.py`.
2. Add its schema in `TOOLS`.
3. Register it in `tool_registry`.

### Running tests

```bash
python main.py
```

## Troubleshooting

- Missing env vars: set `MODEL` and `API_KEY` in `.env`.
- LLM call fails: check key, model name, and network.
- File errors: verify path and permissions.

## License
Open source.

## Contributing
Pull requests welcome.

## Acknowledgments
- [litellm](https://github.com/BerriAI/litellm)
- [uv](https://github.com/astral-sh/uv)
