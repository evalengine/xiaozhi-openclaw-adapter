import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import type { XiaozhiWebSocketClient } from "../client/websocket.js";
export declare const xiaozhiSendMessageTool: (client: XiaozhiWebSocketClient, api: OpenClawPluginApi) => {
    name: string;
    description: string;
    parameters: import("@sinclair/typebox").TObject<{
        to: import("@sinclair/typebox").TString;
        text: import("@sinclair/typebox").TString;
        channel: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
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
//# sourceMappingURL=send-message.d.ts.map