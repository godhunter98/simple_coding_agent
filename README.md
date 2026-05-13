# Simple Coding Agent

A lightweight CLI coding assistant powered by LLMs via [litellm](https://github.com/BerriAI/litellm).

<img width="2048" height="1332" alt="image" src="https://github.com/user-attachments/assets/01562b90-952e-4d57-83c4-df1218f09999" />


## Features

- 5 tools: read, list, edit files · run bash commands · run bash scripts
- Provider-agnostic — works with OpenAI, Anthropic, Gemini, DeepSeek, local models
- Safety checks on shell commands with warn + confirm prompt
- Animated terminal UI — block-letter banner, braille spinner
- Bunch of tests to test functionality

## Installation

```bash
git clone <repository-url>
cd simple-coding-agent
uv sync
```

Or with pip: `pip install -e .`

## Configuration

Create a `.env` file:

```env
MODEL="deepseek/deepseek-coder"
API_KEY="your-api-key-here"
API_BASE="http://localhost:8000/v1"  # optional, for local models
```

Any model supported by litellm works.

## Usage

```bash
uv run python main.py
# or
python main.py
```

Type `exit`, `quit`, or press `Ctrl+C` to quit.

## Project structure

```
simple-coding-agent/
├── main.py           # entrypoint
├── coding_agent.py   # agent loop + LLM calls
├── tools.py          # tool definitions + safety checks
├── prompts.py        # system prompt
├── animation.py      # banner + spinner
├── ui.py             # colors + icons
└── pyproject.toml
```

## Adding new tools

1. Add a function in `tools.py`
2. Add its schema to `TOOLS`
3. Register it in `tool_registry` in `coding_agent.py`

## Troubleshooting

- Missing env vars → set `MODEL` and `API_KEY` in `.env`
- LLM call fails → check API key, model name, and network
- File errors → verify path and permissions
