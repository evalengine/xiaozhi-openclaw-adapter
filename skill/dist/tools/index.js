import { xiaozhiSendMessageTool } from "./send-message.js";
import { xiaozhiDeviceControlTool } from "./device-control.js";
import { xiaozhiAgentTaskTool } from "./agent-task.js";
import { xiaozhiListDevicesTool } from "./list-devices.js";
export function registerXiaozhiTools(client, api) {
    api.registerTool(xiaozhiSendMessageTool(client, api));
    api.registerTool(xiaozhiDeviceControlTool(client, api));
    api.registerTool(xiaozhiAgentTaskTool(client, api));
    api.registerTool(xiaozhiListDevicesTool(client, api));
}
export { xiaozhiSendMessageTool, xiaozhiDeviceControlTool, xiaozhiAgentTaskTool, xiaozhiListDevicesTool };
