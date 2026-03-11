import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import type { XiaozhiWebSocketClient } from "../client/websocket.js";
export declare const xiaozhiAgentTaskTool: (client: XiaozhiWebSocketClient, api: OpenClawPluginApi) => {
    name: string;
    description: string;
    parameters: import("@sinclair/typebox").TObject<{
        action: import("@sinclair/typebox").TUnsafe<"execute" | "status" | "cancel">;
        taskId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
        prompt: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
        device_id: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
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
//# sourceMappingURL=agent-task.d.ts.map