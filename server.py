import asyncio
import sys

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from agent import Agent

agent = Agent()
server = agent.server


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return await agent.handle_list_tools()


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    return await agent.handle_call_tool()


async def main():
    print(r"""
     ______   ______   _________  ________  ___ __ __   __  __   ______      
    /_____/\ /_____/\ /________/\/_______/\/__//_//_/\ /_/\/_/\ /_____/\     
    \:::_ \ \\:::_ \ \\__.::.__\/\__.::._\/\::\| \| \ \\:\ \:\ \\::::_\/_    
     \:\ \ \ \\:(_) \ \  \::\ \     \::\ \  \:.      \ \\:\ \:\ \\:\/___/\   
      \:\ \ \ \\: ___\/   \::\ \    _\::\ \__\:.\-/\  \ \\:\ \:\ \\_::._\:\  
       \:\_\ \ \\ \ \      \::\ \  /__\::\__/\\. \  \  \ \\:\_\:\ \ /____\:\ 
        \_____\/ \_\/       \__\/  \________\/ \__\/ \__\/ \_____\/ \_____\/ 
        Optimus MCP server | @brightseid | v0.0.1
    """, file=sys.stderr)

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="Optimus",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
