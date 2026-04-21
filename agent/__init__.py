import os
import subprocess
import sys

from mcp.server import Server
import mcp.types as types
import load_config


class Agent:
    def __init__(self):
        self.config = load_config.load_json_data()
        self.server = Server("Optimus")
        self.workdir = self.config["workdir"]

    def safe_path(self, relative_path: str) -> str:
        workspace = os.path.abspath(self.workdir)
        abs_path = os.path.abspath(os.path.join(workspace, relative_path))

        if os.path.commonpath([workspace, abs_path]) != workspace:
            raise ValueError(f"Access denied: {relative_path} is outside the workspace directory")

        return abs_path

    async def handle_list_tools(self) -> list[types.Tool]:
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
            ),

            types.Tool(
                name="command_run",
                description="Run command inside the project directory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Relative path from workspace root"},
                        "command": {"type": "string", "description": "Command to run"}
                    },
                    "required": ["path", "command"]
                }
            )
        ]

    async def handle_call_tool(self, name: str, arguments: dict) -> list[types.TextContent]:
        if name == "read_file":
            print("File read tool selected", file=sys.stderr)
            path = self.safe_path(arguments["path"])
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    return [types.TextContent(type="text", text=content)]
            except Exception as e:
                return [types.TextContent(type="text", text=f"Error reading file: {str(e)}")]

        elif name == "write_file":
            print("File write tool selected", file=sys.stderr)
            path = self.safe_path(arguments["path"])
            content = arguments["content"]
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return [types.TextContent(type="text", text=f"Successfully wrote to {path}")]
            except Exception as e:
                return [types.TextContent(type="text", text=f"Error writing file: {str(e)}")]

        elif name == "command_run":
            result = subprocess.run(
                arguments["command"],
                shell=not self.config["safe"],
                cwd=self.safe_path(arguments["path"]),
                capture_output=True,
                text=True
            )
            output = result.stdout + result.stderr
            return [types.TextContent(type="text", text=output)]

        else:
            raise ValueError(f"Unknown tool: {name}")
