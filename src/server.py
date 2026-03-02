"""MCP Server for A-Share market analysis."""

import asyncio
import logging
import sys
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import (
    TextContent,
    Tool,
    CallToolResult,
)
from mcp.server.stdio import stdio_server

# Import our tools
from .tools import get_realtime_quotes, get_market_news, generate_stock_analysis_report, generate_professional_analysis_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def handle_get_realtime_quotes(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle get_realtime_quotes tool call."""
    try:
        symbol = arguments.get("symbol")
        if not symbol:
            raise ValueError("Symbol is required")
            
        logger.info(f"Handling get_realtime_quotes request for symbol: {symbol}")
        result = get_realtime_quotes(symbol)
        
        return CallToolResult(
            content=[TextContent(type="text", text=str(result))]
        )
        
    except Exception as e:
        logger.error(f"Error in get_realtime_quotes: {str(e)}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )


async def handle_get_market_news(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle get_market_news tool call."""
    try:
        symbol = arguments.get("symbol")
        max_results = arguments.get("max_results", 5)
        
        if not symbol:
            raise ValueError("Symbol is required")
            
        logger.info(f"Handling get_market_news request for symbol: {symbol}")
        result = get_market_news(symbol, max_results=max_results)
        
        return CallToolResult(
            content=[TextContent(type="text", text=str(result))]
        )
        
    except Exception as e:
        logger.error(f"Error in get_market_news: {str(e)}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )


async def handle_generate_stock_analysis_report(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle generate_stock_analysis_report tool call."""
    try:
        symbol = arguments.get("symbol")
        if not symbol:
            raise ValueError("Symbol is required")
            
        logger.info(f"Handling generate_stock_analysis_report request for symbol: {symbol}")
        result = generate_stock_analysis_report(symbol)
        
        return CallToolResult(
            content=[TextContent(type="text", text=str(result))]
        )
        
    except Exception as e:
        logger.error(f"Error in generate_stock_analysis_report: {str(e)}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )


async def handle_stock_analysis_tool(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle stock_analysis_tool (primary professional analysis) tool call."""
    try:
        symbol = arguments.get("symbol")
        if not symbol:
            raise ValueError("Symbol is required")
            
        logger.info(f"Handling stock_analysis_tool request for symbol: {symbol}")
        result = generate_professional_analysis_report(symbol)
        
        return CallToolResult(
            content=[TextContent(type="text", text=str(result))]
        )
        
    except Exception as e:
        logger.error(f"Error in stock_analysis_tool: {str(e)}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )


async def run_server():
    """Run the MCP server using stdio transport."""
    server = Server("ashare-mcp-agent")
    
    # Register stock_analysis_tool (primary tool with consistent naming)
    @server.call_tool()
    async def stock_analysis_tool(symbol: str) -> CallToolResult:
        return await handle_stock_analysis_tool({"symbol": symbol})
    
    # Register legacy tools for compatibility
    @server.call_tool()
    async def generate_stock_analysis_report(symbol: str) -> CallToolResult:
        return await handle_generate_stock_analysis_report({"symbol": symbol})
    
    @server.call_tool()
    async def get_realtime_quotes(symbol: str) -> CallToolResult:
        return await handle_get_realtime_quotes({"symbol": symbol})
    
    @server.call_tool()
    async def get_market_news(symbol: str, max_results: int = 5) -> CallToolResult:
        return await handle_get_market_news({"symbol": symbol, "max_results": max_results})
    
    logger.info("Starting A-Share MCP Server...")
    await stdio_server(server)


def main():
    """Main entry point for the MCP server."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()