import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def serverTest():
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            tools = tools_result.tools

            print("Available tools:", [t.name for t in tools])

            call_result = await session.call_tool("read_file", {"path": "index.html"})
            print("File content:", call_result.content)


asyncio.run(serverTest())
