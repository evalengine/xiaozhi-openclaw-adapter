import { Type } from "@sinclair/typebox";
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import type { XiaozhiWebSocketClient } from "../client/websocket.js";

export const xiaozhiListDevicesTool = (client: XiaozhiWebSocketClient, api: OpenClawPluginApi) => ({
  name: "xiaozhi_list_devices",
  description: "List all ESP32 devices currently connected to the xiaozhi server, including their MAC addresses, IPs, and session info",
  parameters: Type.Object({}),
  async execute(_id: string, _params: Record<string, unknown>) {
    if (!client.isConnected()) {
      return { content: [{ type: "text", text: "xiaozhi 服务器当前未连接，请检查服务器是否运行。" }], isError: true };
    }

    api.logger.info("xiaozhi_list_devices: fetching connected devices");
    const result = await client.callMethod("devices/list");
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }], details: result };
  },
});
