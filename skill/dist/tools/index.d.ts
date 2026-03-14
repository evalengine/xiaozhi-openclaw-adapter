import type { XiaozhiWebSocketClient } from "../client/websocket.js";
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { xiaozhiSendMessageTool } from "./send-message.js";
import { xiaozhiDeviceControlTool } from "./device-control.js";
import { xiaozhiAgentTaskTool } from "./agent-task.js";
import { xiaozhiListDevicesTool } from "./list-devices.js";
export declare function registerXiaozhiTools(client: XiaozhiWebSocketClient, api: OpenClawPluginApi): void;
export { xiaozhiSendMessageTool, xiaozhiDeviceControlTool, xiaozhiAgentTaskTool, xiaozhiListDevicesTool };
//# sourceMappingURL=index.d.ts.map