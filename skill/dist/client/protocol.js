export const JsonRpcErrorCodes = {
    ParseError: -32700,
    InvalidRequest: -32600,
    MethodNotFound: -32601,
    InvalidParams: -32602,
    InternalError: -32603,
};
export function createToolCallRequest(id, toolName, args) {
    return { jsonrpc: "2.0", id, method: "tools/call", params: { name: toolName, arguments: args } };
}
export function createHeartbeatRequest(id) {
    return { jsonrpc: "2.0", id, method: "ping" };
}
export function createMethodRequest(id, method, params = {}) {
    return { jsonrpc: "2.0", id, method, params };
}
export function isErrorResponse(r) {
    return "error" in r;
}
export function isSuccessResponse(r) {
    return "result" in r;
}
export function extractToolResult(response) {
    if (isErrorResponse(response)) {
        return { success: false, error: response.error.message };
    }
    const result = response.result;
    if (typeof result === "object" && result !== null && "success" in result) {
        return result;
    }
    return { success: true, data: result };
}
export function parseJsonRpcMessage(message) {
    try {
        const parsed = JSON.parse(message);
        if (typeof parsed === "object" && parsed !== null && parsed.jsonrpc === "2.0") {
            return parsed;
        }
        return null;
    }
    catch {
        return null;
    }
}
export function stringifyJsonRpcMessage(message) {
    return JSON.stringify(message);
}
