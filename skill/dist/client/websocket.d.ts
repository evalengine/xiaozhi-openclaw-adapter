import type { ConnectionState, ToolCallResult, ClientEvents, XiaozhiPluginConfig } from "../types.js";
export declare class XiaozhiWebSocketClient {
    private config;
    private ws;
    private state;
    private pendingRequests;
    private requestId;
    private reconnectAttempts;
    private reconnectTimer;
    private heartbeatTimer;
    private connectionTimer;
    private eventHandlers;
    private isManualClose;
    constructor(config: XiaozhiPluginConfig);
    on<K extends keyof ClientEvents>(event: K, handler: ClientEvents[K]): void;
    getState(): ConnectionState;
    isConnected(): boolean;
    connect(): Promise<void>;
    disconnect(): void;
    callTool(toolName: string, args: Record<string, unknown>): Promise<ToolCallResult>;
    private send;
    private handleMessage;
    private handleDisconnect;
    private scheduleReconnect;
    private stopReconnect;
    private startHeartbeat;
    private stopHeartbeat;
    private clearConnectionTimer;
    private cleanup;
    private setState;
    private emit;
}
//# sourceMappingURL=websocket.d.ts.map