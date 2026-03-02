# Tool Naming Convention

## Primary Tool Name
**`stock_analysis_tool`** - This is the official, consistent name for the main stock analysis functionality.

## Naming Rules
1. **DO NOT** change the primary tool name `stock_analysis_tool`
2. **DO NOT** rename this tool in future updates
3. **DO** use this exact name for reliable integration with LLM clients
4. **DO** maintain backward compatibility with legacy tool names

## Tool Mapping
- `stock_analysis_tool` → `generate_professional_analysis_report()` (primary)
- `generate_stock_analysis_report` → `generate_stock_analysis_report()` (legacy)

## Integration Instructions
When configuring MCP servers in Claude Desktop or other LLM clients, always reference the tool as:
```
stock_analysis_tool
```

This ensures consistent and reliable tool calling across all versions.