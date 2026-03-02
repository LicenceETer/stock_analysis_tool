# A-Share MCP Agent

An MCP (Model Context Protocol) server for Chinese A-share market analysis, providing real-time stock data, news, and technical analysis capabilities to LLMs.

## Features

- Real-time stock quotes via AKShare
- Financial news aggregation from major Chinese portals
- Technical indicator calculation (MA5, MA20, RSI, etc.)
- Structured analysis reports for LLM consumption

## Requirements

- Python 3.10+
- Dependencies listed in `pyproject.toml`

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd ashare-mcp-agent

# Install dependencies (using uv recommended)
uv sync --all-extras

# Or using pip
pip install -e .
```

## Running with Claude Desktop

1. Start the MCP server:
   ```bash
   python -m src.server
   ```

2. In Claude Desktop, add a new MCP server with the following configuration:
   - **Name**: A-Share Analysis Agent
   - **Transport**: stdio
   - **Command**: `python -m src.server`

3. The agent will now be available for use in your conversations.

## Available Tools

### `get_realtime_quotes`
Fetch real-time price, volume, and trading data for a specific stock.

**Input**: Stock code (e.g., "600519" for 贵州茅台)

### `get_market_news`
Retrieve recent financial news and sentiment for a stock or keyword.

**Input**: Stock code or keywords

### `generate_stock_analysis_report`
Generate a comprehensive analysis report combining market data and news.

**Input**: Stock code

## Project Structure

```
ashare-mcp-agent/
├── src/
│   ├── __init__.py
│   ├── server.py          # Main MCP server entry point
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── market_data.py # Real-time data fetching
│   │   ├── news.py        # News aggregation
│   │   └── analysis.py    # Technical analysis
│   └── utils/
│       └── formatters.py  # Data formatting helpers
├── tests/                 # Unit tests
├── pyproject.toml         # Project metadata and dependencies
└── README.md              # This file
```