import { WebSocket } from "ws";
import { createToolCallRequest, createHeartbeatRequest, createMethodRequest, extractToolResult, parseJsonRpcMessage, stringifyJsonRpcMessage, } from "./protocol.js";
export class XiaozhiWebSocketClient {
    config;
    ws = null;
    state = "disconnected";
    pendingRequests = new Map();
    requestId = 0;
    reconnectAttempts = 0;
    reconnectTimer = null;
    heartbeatTimer = null;
    connectionTimer = null;
    eventHandlers = {};
    isManualClose = false;
    constructor(config) {
        this.config = config;
    }
    on(event, handler) {
        this.eventHandlers[event] = handler;
    }
    getState() { return this.state; }
    isConnected() {
        return this.state === "connected" && this.ws?.readyState === WebSocket.OPEN;
    }
    connect() {
        return new Promise((resolve, reject) => {
            if (this.isConnected()) {
                resolve();
                return;
            }
            this.isManualClose = false;
            this.setState("connecting");
            try {
                const headers = {};
                if (this.config.authToken)
                    headers["Authorization"] = `Bearer ${this.config.authToken}`;
                this.ws = new WebSocket(this.config.serverUrl, { headers });
                const timeoutMs = this.config.connectionTimeout ?? 10000;
                this.connectionTimer = setTimeout(() => {
                    if (this.state === "connecting") {
                        this.cleanup();
                        const err = new Error(`Connection timeout after ${timeoutMs}ms`);
                        this.setState("error");
                        this.emit("error", err);
                        reject(err);
                    }
                }, timeoutMs);
                this.ws.on("open", () => {
                    this.clearConnectionTimer();
                    this.setState("connected");
                    this.reconnectAttempts = 0;
                    this.startHeartbeat();
                    this.emit("connect");
                    resolve();
                });
                this.ws.on("message", (data) => this.handleMessage(data.toString("utf8")));
                this.ws.on("error", (error) => {
                    this.clearConnectionTimer();
                    this.setState("error");
                    this.emit("error", error);
                    reject(error);
                });
                this.ws.on("close", (code, reason) => {
                    this.clearConnectionTimer();
                    this.handleDisconnect(code, reason.toString("utf8"));
                });
            }
            catch (error) {
                this.clearConnectionTimer();
                this.setState("error");
                reject(error);
            }
        });
    }
    disconnect() {
        this.isManualClose = true;
        this.stopHeartbeat();
        this.stopReconnect();
        this.cleanup();
        this.setState("disconnected");
    }
    async callTool(toolName, args) {
        if (!this.isConnected())
            return { success: false, error: "Not connected to xiaozhi server" };
        const id = ++this.requestId;
        return new Promise((resolve, reject) => {
            const timer = setTimeout(() => {
                this.pendingRequests.delete(id);
                reject(new Error(`Tool call timeout: ${toolName}`));
            }, 30000);
            this.pendingRequests.set(id, {
                resolve: (r) => { clearTimeout(timer); resolve(r); },
                reject: (e) => { clearTimeout(timer); reject(e); },
            });
            this.send(createToolCallRequest(id, toolName, args));
        });
    }
    async callMethod(method, params = {}) {
        if (!this.isConnected())
            return { success: false, error: "Not connected to xiaozhi server" };
        const id = ++this.requestId;
        return new Promise((resolve, reject) => {
            const timer = setTimeout(() => {
                this.pendingRequests.delete(id);
                reject(new Error(`Method call timeout: ${method}`));
            }, 30000);
            this.pendingRequests.set(id, {
                resolve: (r) => { clearTimeout(timer); resolve(r); },
                reject: (e) => { clearTimeout(timer); reject(e); },
            });
            this.send(createMethodRequest(id, method, params));
        });
    }
    send(request) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN)
            return;
        try {
            this.ws.send(stringifyJsonRpcMessage(request));
        }
        catch (error) {
            this.emit("error", error);
        }
    }
    handleMessage(message) {
        const parsed = parseJsonRpcMessage(message);
        if (!parsed)
            return;
        if ("result" in parsed || "error" in parsed) {
            const response = parsed;
            const pending = this.pendingRequests.get(response.id);
            if (pending) {
                this.pendingRequests.delete(response.id);
                pending.resolve(extractToolResult(response));
            }
        }
        else {
            this.emit("message", parsed);
        }
    }
    handleDisconnect(code, reason) {
        this.stopHeartbeat();
        this.cleanup();
        for (const [, pending] of this.pendingRequests) {
            pending.reject(new Error(`Connection closed: ${reason}`));
        }
        this.pendingRequests.clear();
        this.emit("disconnect", code, reason);
        if (!this.isManualClose)
            this.scheduleReconnect();
    }
    scheduleReconnect() {
        const maxAttempts = this.config.maxReconnectAttempts ?? 10;
        if (this.reconnectAttempts >= maxAttempts) {
            this.setState("error");
            this.emit("reconnectFailed");
            // Keep retrying indefinitely after max attempts
            this.reconnectAttempts = 0;
        }
        this.reconnectAttempts++;
        this.setState("reconnecting");
        this.emit("reconnect", this.reconnectAttempts);
        this.reconnectTimer = setTimeout(() => {
            this.connect().catch((e) => this.emit("error", e));
        }, this.config.reconnectInterval ?? 5000);
    }
    stopReconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
    }
    startHeartbeat() {
        this.stopHeartbeat();
        this.heartbeatTimer = setInterval(() => {
            if (this.isConnected())
                this.send(createHeartbeatRequest(++this.requestId));
        }, this.config.heartbeatInterval ?? 30000);
    }
    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }
    clearConnectionTimer() {
        if (this.connectionTimer) {
            clearTimeout(this.connectionTimer);
            this.connectionTimer = null;
        }
    }
    cleanup() {
        if (this.ws) {
            this.ws.removeAllListeners();
            if (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING) {
                this.ws.close();
            }
            this.ws = null;
        }
    }
    setState(state) { this.state = state; }
    emit(event, ...args) {
        const handler = this.eventHandlers[event];
        if (handler)
            handler(...args);
    }
}
