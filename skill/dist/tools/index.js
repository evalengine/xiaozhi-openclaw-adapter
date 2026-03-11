import { xiaozhiSendMessageTool } from "./send-message.js";
import { xiaozhiDeviceControlTool } from "./device-control.js";
import { xiaozhiAgentTaskTool } from "./agent-task.js";
export function registerXiaozhiTools(client, api) {
    api.registerTool(xiaozhiSendMessageTool(client, api));
    api.registerTool(xiaozhiDeviceControlTool(client, api));
    api.registerTool(xiaozhiAgentTaskTool(client, api));
}
export { xiaozhiSendMessageTool, xiaozhiDeviceControlTool, xiaozhiAgentTaskTool };
