import asyncio
import os
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

server = Server("your-server-name")

WORKSPACE = "your workspace dir"


def safe_path(relative_path: str) -> str:
    workspace = os.path.abspath(WORKSPACE)
    abs_path = os.path.abspath(os.path.join(workspace, relative_path))

    if os.path.commonpath([workspace, abs_path]) != workspace:
        raise ValueError(f"Access denied: {relative_path} is outside the workspace directory")

    return abs_path


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="read_file",
            description="Read contents of a file from the project",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path from workspace root"}
                },
                "required": ["path"]
            }
        ),

        types.Tool(
            name="write_file",
            description="Write contents to a file in the project",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path from workspace root"},
                    "content": {"type": "string", "description": "Content to write"}
                },
                "required": ["path", "content"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name:str, arguments: dict)-> list[types.TextContent]:
    if name == "read_file":
        path = safe_path(arguments["path"])
        try:
            with open(path,"r", encoding="utf-8") as f:
                content = f.read()
                return [types.TextContent(type="text", text=content)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error reading file: {str(e)}")]

    elif name == "write_file":
        path = safe_path(arguments["path"])
        content = arguments["content"]
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return [types.TextContent(type="text", text=f"Successfully wrote to {path}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error writing file: {str(e)}")]

    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="your-server-name",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
