import type {
  JsonRpcRequest,
  JsonRpcResponse,
  JsonRpcResponseSuccess,
  JsonRpcResponseError,
  ToolCallResult,
} from "../types.js";

export const JsonRpcErrorCodes = {
  ParseError: -32700,
  InvalidRequest: -32600,
  MethodNotFound: -32601,
  InvalidParams: -32602,
  InternalError: -32603,
} as const;

export function createToolCallRequest(
  id: number,
  toolName: string,
  args: Record<string, unknown>,
): JsonRpcRequest {
  return { jsonrpc: "2.0", id, method: "tools/call", params: { name: toolName, arguments: args } };
}

export function createHeartbeatRequest(id: number): JsonRpcRequest {
  return { jsonrpc: "2.0", id, method: "ping" };
}

export function isErrorResponse(r: JsonRpcResponse): r is JsonRpcResponseError {
  return "error" in r;
}

export function isSuccessResponse(r: JsonRpcResponse): r is JsonRpcResponseSuccess {
  return "result" in r;
}

export function extractToolResult(response: JsonRpcResponse): ToolCallResult {
  if (isErrorResponse(response)) {
    return { success: false, error: response.error.message };
  }
  const result = response.result;
  if (typeof result === "object" && result !== null && "success" in result) {
    return result as ToolCallResult;
  }
  return { success: true, data: result };
}

export function parseJsonRpcMessage(message: string): JsonRpcRequest | JsonRpcResponse | null {
  try {
    const parsed = JSON.parse(message);
    if (typeof parsed === "object" && parsed !== null && parsed.jsonrpc === "2.0") {
      return parsed as JsonRpcRequest | JsonRpcResponse;
    }
    return null;
  } catch {
    return null;
  }
}

export function stringifyJsonRpcMessage(message: JsonRpcRequest | JsonRpcResponse): string {
  return JSON.stringify(message);
}
