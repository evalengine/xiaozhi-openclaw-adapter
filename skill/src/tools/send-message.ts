import { Type } from "@sinclair/typebox";
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import type { XiaozhiWebSocketClient } from "../client/websocket.js";

export const xiaozhiSendMessageTool = (client: XiaozhiWebSocketClient, api: OpenClawPluginApi) => ({
  name: "xiaozhi_send_message",
  description: "Send a message to a configured messaging channel (Telegram, Discord, WeChat, etc.) through the xiaozhi server",
  parameters: Type.Object({
    to: Type.String({ description: "Recipient identifier (user ID, chat ID, phone number, etc.)" }),
    text: Type.String({ description: "Message content to send" }),
    channel: Type.Optional(Type.String({ description: "Channel name (telegram, discord, wechat, etc.). Uses default channel if not specified." })),
  }),
  async execute(_id: string, params: Record<string, unknown>) {
    if (!client.isConnected()) {
      return { content: [{ type: "text", text: "xiaozhi 服务器当前未连接，请检查服务器是否运行。" }], isError: true };
    }
    const { to, text, channel } = params as { to: string; text: string; channel?: string };
    if (!to) throw new Error("Recipient (to) is required");
    if (!text) throw new Error("Message text is required");

    api.logger.info(`xiaozhi_send_message: to=${to}, channel=${channel ?? "default"}`);
    const args: Record<string, unknown> = { to, text };
    if (channel) args.channel = channel;

    const result = await client.callTool("xiaozhi_send_message", args);
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }], details: result };
  },
});
