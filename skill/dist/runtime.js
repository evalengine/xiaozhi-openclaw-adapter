import { XiaozhiWebSocketClient } from "./client/websocket.js";
import { registerXiaozhiTools } from "./tools/index.js";
import { XiaozhiPluginConfigSchema } from "./config/schema.js";
import { DEFAULT_CONFIG } from "./config/types.js";
let client = null;
function loadConfig(api) {
    const rawConfig = { ...DEFAULT_CONFIG, ...(api.pluginConfig ?? {}) };
    const result = XiaozhiPluginConfigSchema.safeParse(rawConfig);
    if (!result.success) {
        const errors = result.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`);
        throw new Error(`Invalid plugin configuration:\n${errors.join("\n")}`);
    }
    return result.data;
}
export async function startPlugin(api) {
    if (client) {
        api.logger.warn("xiaozhi: Plugin already started");
        return;
    }
    try {
        const config = loadConfig(api);
        const ws = new XiaozhiWebSocketClient(config);
        ws.on("connect", () => { api.logger.info("xiaozhi: Connected to server"); });
        ws.on("disconnect", (code, reason) => { api.logger.info(`xiaozhi: Disconnected (${code}): ${reason}`); });
        ws.on("error", (error) => { api.logger.error(`xiaozhi: Error: ${error.message}`); });
        ws.on("reconnect", (attempt) => { api.logger.info(`xiaozhi: Reconnecting (attempt ${attempt})`); });
        ws.on("reconnectFailed", () => { api.logger.warn("xiaozhi: Max reconnect attempts reached, continuing to retry..."); });
        client = ws;
        registerXiaozhiTools(ws, api);
        api.logger.info(`xiaozhi: Tools registered, connecting to ${config.serverUrl}`);
        ws.connect().catch((err) => {
            api.logger.warn(`xiaozhi: Initial connection failed: ${err.message}, retrying in background`);
        });
    }
    catch (err) {
        api.logger.error(`xiaozhi: Failed to start: ${err instanceof Error ? err.message : String(err)}`);
    }
}
export async function stopPlugin(api) {
    if (client) {
        api.logger.info("xiaozhi: Stopping plugin");
        client.disconnect();
        client = null;
    }
}
export function getClient() { return client; }
