/**
 * Shared types for xiaozhi-openclaw plugin
 */

export interface XiaozhiWebSocketClientLike {
  isConnected(): boolean;
}

export interface JsonRpcRequest {
  jsonrpc: "2.0";
  id: number | string;
  method: string;
  params?: unknown;
}

export interface JsonRpcResponseSuccess {
  jsonrpc: "2.0";
  id: number | string;
  result: unknown;
}

export interface JsonRpcResponseError {
  jsonrpc: "2.0";
  id: number | string;
  error: {
    code: number;
    message: string;
    data?: unknown;
  };
}

export type JsonRpcResponse = JsonRpcResponseSuccess | JsonRpcResponseError;

export interface ToolCallParams {
  name: string;
  arguments: Record<string, unknown>;
}

export interface ToolCallResult {
  success: boolean;
  data?: unknown;
  error?: string;
}

export type ConnectionState =
  | "disconnected"
  | "connecting"
  | "connected"
  | "reconnecting"
  | "error";

export interface ClientEvents {
  connect: () => void;
  disconnect: (code: number, reason: string) => void;
  error: (error: Error) => void;
  message: (message: JsonRpcRequest | JsonRpcResponse) => void;
  reconnect: (attempt: number) => void;
  reconnectFailed: () => void;
}

export interface XiaozhiPluginConfig {
  serverUrl: string;
  authToken?: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
  connectionTimeout?: number;
}
