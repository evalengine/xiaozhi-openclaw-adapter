import type { JsonRpcRequest, JsonRpcResponse, JsonRpcResponseSuccess, JsonRpcResponseError, ToolCallResult } from "../types.js";
export declare const JsonRpcErrorCodes: {
    readonly ParseError: -32700;
    readonly InvalidRequest: -32600;
    readonly MethodNotFound: -32601;
    readonly InvalidParams: -32602;
    readonly InternalError: -32603;
};
export declare function createToolCallRequest(id: number, toolName: string, args: Record<string, unknown>): JsonRpcRequest;
export declare function createHeartbeatRequest(id: number): JsonRpcRequest;
export declare function isErrorResponse(r: JsonRpcResponse): r is JsonRpcResponseError;
export declare function isSuccessResponse(r: JsonRpcResponse): r is JsonRpcResponseSuccess;
export declare function extractToolResult(response: JsonRpcResponse): ToolCallResult;
export declare function parseJsonRpcMessage(message: string): JsonRpcRequest | JsonRpcResponse | null;
export declare function stringifyJsonRpcMessage(message: JsonRpcRequest | JsonRpcResponse): string;
//# sourceMappingURL=protocol.d.ts.map