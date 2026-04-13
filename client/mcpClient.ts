import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import readline from "readline/promises";
import dotenv from "dotenv";
import OpenAI from "openai";

dotenv.config();

const API_KEY = process.env.API_KEY;
if (!API_KEY) {
  throw new Error("API_KEY is not set");
}

export class MCPClient {
  private mcp: Client;
  private client: OpenAI;
  private transport: StdioClientTransport | null = null;
  private tools: any[] = [];

  constructor() {
    this.client = new OpenAI({
      baseURL: "https://openrouter.ai/api/v1",
      apiKey: API_KEY,
    });
    this.mcp = new Client({ name: "mcp-client-cli", version: "1.0.0" });
  }

  async connectToServer(serverScriptPath: string) {
    try {
      const isJs = serverScriptPath.endsWith(".js");
      const isPy = serverScriptPath.endsWith(".py");
      if (!isJs && !isPy) {
        throw new Error("Server script must be a .js or .py file");
      }

      const command = isPy
        ? process.platform === "win32"
          ? "python"
          : "python3"
        : process.execPath;

      this.transport = new StdioClientTransport({
        command,
        args: [serverScriptPath],
      });
      await this.mcp.connect(this.transport);

      const toolsResult = await this.mcp.listTools();

      this.tools = toolsResult.tools.map((tool) => ({
        type: "function",
        function: {
          name: tool.name,
          description: tool.description ?? "",
          parameters: tool.inputSchema,
        },
      }));

      console.log(
        "Connected to server with tools:",
        toolsResult.tools.map((t) => t.name),
      );
    } catch (e) {
      console.log("Failed to connect to MCP server: ", e);
      throw e;
    }
  }

  async processQuery(query: string) {
    const messages: any[] = [{ role: "user", content: query }];
    const finalText: string[] = [];

    const response = await this.client.chat.completions.create({
      model: "openai/gpt-oss-120b:free",
      messages,
      tools: this.tools,
    });

    const message = response.choices[0].message as any;

    if (message.content) {
      finalText.push(message.content);
    }

    if (message.tool_calls && message.tool_calls.length > 0) {
      messages.push({
        role: "assistant",
        content: message.content ?? null,
        tool_calls: message.tool_calls,
      });

      for (const toolCall of message.tool_calls) {
        const toolName: string = toolCall.function.name;
        const toolArgs = JSON.parse(toolCall.function.arguments);

        finalText.push(
          `[Calling tool ${toolName} with args ${JSON.stringify(toolArgs)}]`,
        );

        const result = await this.mcp.callTool({
          name: toolName,
          arguments: toolArgs,
        });

        messages.push({
          role: "tool",
          tool_call_id: toolCall.id,
          content: JSON.stringify(result.content),
        });
      }

      const followUp = await this.client.chat.completions.create({
        model: "meta-llama/llama-3.1-8b-instruct",
        messages,
        tools: this.tools,
        max_tokens: 10,
        max_completion_tokens: 10,
      });

      finalText.push((followUp.choices[0].message as any).content ?? "");
    }

    return finalText.join("\n");
  }

  async chatLoop() {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    try {
      console.log("\nMCP Client Started!");
      console.log("Type your queries or 'quit' to exit.");

      while (true) {
        const message = await rl.question("\nYou: ");
        if (message.toLowerCase() === "quit") break;

        try {
          const response = await this.processQuery(message);
          console.log("\nOptimus:", response);
        } catch (e) {
          console.error("Query error:", e);
        }
      }
    } finally {
      rl.close();
    }
  }

  async cleanup() {
    await this.mcp.close();
  }
}
