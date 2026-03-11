import { Type } from "@sinclair/typebox";
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import type { XiaozhiWebSocketClient } from "../client/websocket.js";

export const xiaozhiDeviceControlTool = (client: XiaozhiWebSocketClient, api: OpenClawPluginApi) => ({
  name: "xiaozhi_device_control",
  description: "Control IoT devices connected to the xiaozhi server (turn on/off, toggle, set value)",
  parameters: Type.Object({
    deviceId: Type.String({ description: "Device identifier (e.g., 'light_01', 'switch_bedroom')" }),
    action: Type.Unsafe<"turn_on" | "turn_off" | "toggle" | "set_value">({
      type: "string", enum: ["turn_on", "turn_off", "toggle", "set_value"],
      description: "Action to perform on the device",
    }),
    value: Type.Optional(Type.Number({
      description: "Value to set (0-100, for set_value action only)",
      minimum: 0, maximum: 100,
    })),
    xiaozhi_device_id: Type.Optional(Type.String({
      description: "Target xiaozhi device MAC address. Uses adapter's defaultDeviceId if not set.",
    })),
  }),
  async execute(_id: string, params: Record<string, unknown>) {
    if (!client.isConnected()) {
      return { content: [{ type: "text", text: "xiaozhi 服务器当前未连接，请检查服务器是否运行。" }], isError: true };
    }
    const { deviceId, action, value, xiaozhi_device_id } = params as {
      deviceId: string; action: string; value?: number; xiaozhi_device_id?: string;
    };
    if (!deviceId) throw new Error("Device ID is required");
    if (!action) throw new Error("Action is required");

    api.logger.info(`xiaozhi_device_control: device=${deviceId}, action=${action}`);
    const args: Record<string, unknown> = { deviceId, action };
    if (value !== undefined) args.value = value;
    if (xiaozhi_device_id) args.xiaozhi_device_id = xiaozhi_device_id;

    const result = await client.callTool("xiaozhi_device_control", args);
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }], details: result };
  },
});
