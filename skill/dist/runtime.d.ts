import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { XiaozhiWebSocketClient } from "./client/websocket.js";
export declare function startPlugin(api: OpenClawPluginApi): Promise<void>;
export declare function stopPlugin(api: OpenClawPluginApi): Promise<void>;
export declare function getClient(): XiaozhiWebSocketClient | null;
//# sourceMappingURL=runtime.d.ts.map