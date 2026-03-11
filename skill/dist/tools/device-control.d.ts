import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import type { XiaozhiWebSocketClient } from "../client/websocket.js";
export declare const xiaozhiDeviceControlTool: (client: XiaozhiWebSocketClient, api: OpenClawPluginApi) => {
    name: string;
    description: string;
    parameters: import("@sinclair/typebox").TObject<{
        deviceId: import("@sinclair/typebox").TString;
        action: import("@sinclair/typebox").TUnsafe<"turn_on" | "turn_off" | "toggle" | "set_value">;
        value: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TNumber>;
        xiaozhi_device_id: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    }>;
    execute(_id: string, params: Record<string, unknown>): Promise<{
        content: {
            type: string;
            text: string;
        }[];
        isError: boolean;
        details?: undefined;
    } | {
        content: {
            type: string;
            text: string;
        }[];
        details: import("../types.js").ToolCallResult;
        isError?: undefined;
    }>;
};
//# sourceMappingURL=device-control.d.ts.map