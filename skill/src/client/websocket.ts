import { WebSocket } from "ws";
import type {
  ConnectionState,
  JsonRpcRequest,
  JsonRpcResponse,
  ToolCallResult,
  ClientEvents,
  XiaozhiPluginConfig,
} from "../types.js";
import {
  createToolCallRequest,
  createHeartbeatRequest,
  extractToolResult,
  parseJsonRpcMessage,
  stringifyJsonRpcMessage,
} from "./protocol.js";

interface PendingRequest {
  resolve: (result: ToolCallResult) => void;
  reject: (error: Error) => void;
}

export class XiaozhiWebSocketClient {
  private ws: WebSocket | null = null;
  private state: ConnectionState = "disconnected";
  private pendingRequests = new Map<number | string, PendingRequest>();
  private requestId = 0;
  private reconnectAttempts = 0;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null;
  private connectionTimer: ReturnType<typeof setTimeout> | null = null;
  private eventHandlers: Partial<ClientEvents> = {};
  private isManualClose = false;

  constructor(private config: XiaozhiPluginConfig) {}

  on<K extends keyof ClientEvents>(event: K, handler: ClientEvents[K]): void {
    this.eventHandlers[event] = handler;
  }

  getState(): ConnectionState { return this.state; }

  isConnected(): boolean {
    return this.state === "connected" && this.ws?.readyState === WebSocket.OPEN;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.isConnected()) { resolve(); return; }

      this.isManualClose = false;
      this.setState("connecting");

      try {
        const headers: Record<string, string> = {};
        if (this.config.authToken) headers["Authorization"] = `Bearer ${this.config.authToken}`;

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

        this.ws.on("message", (data: Buffer) => this.handleMessage(data.toString("utf8")));

        this.ws.on("error", (error: Error) => {
          this.clearConnectionTimer();
          this.setState("error");
          this.emit("error", error);
          reject(error);
        });

        this.ws.on("close", (code: number, reason: Buffer) => {
          this.clearConnectionTimer();
          this.handleDisconnect(code, reason.toString("utf8"));
        });
      } catch (error) {
        this.clearConnectionTimer();
        this.setState("error");
        reject(error);
      }
    });
  }

  disconnect(): void {
    this.isManualClose = true;
    this.stopHeartbeat();
    this.stopReconnect();
    this.cleanup();
    this.setState("disconnected");
  }

  async callTool(toolName: string, args: Record<string, unknown>): Promise<ToolCallResult> {
    if (!this.isConnected()) return { success: false, error: "Not connected to xiaozhi server" };

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

  private send(request: JsonRpcRequest): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    try { this.ws.send(stringifyJsonRpcMessage(request)); }
    catch (error) { this.emit("error", error as Error); }
  }

  private handleMessage(message: string): void {
    const parsed = parseJsonRpcMessage(message);
    if (!parsed) return;

    if ("result" in parsed || "error" in parsed) {
      const response = parsed as JsonRpcResponse;
      const pending = this.pendingRequests.get(response.id);
      if (pending) {
        this.pendingRequests.delete(response.id);
        pending.resolve(extractToolResult(response));
      }
    } else {
      this.emit("message", parsed);
    }
  }

  private handleDisconnect(code: number, reason: string): void {
    this.stopHeartbeat();
    this.cleanup();
    for (const [, pending] of this.pendingRequests) {
      pending.reject(new Error(`Connection closed: ${reason}`));
    }
    this.pendingRequests.clear();
    this.emit("disconnect", code, reason);
    if (!this.isManualClose) this.scheduleReconnect();
  }

  private scheduleReconnect(): void {
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

  private stopReconnect(): void {
    if (this.reconnectTimer) { clearTimeout(this.reconnectTimer); this.reconnectTimer = null; }
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.heartbeatTimer = setInterval(() => {
      if (this.isConnected()) this.send(createHeartbeatRequest(++this.requestId));
    }, this.config.heartbeatInterval ?? 30000);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) { clearInterval(this.heartbeatTimer); this.heartbeatTimer = null; }
  }

  private clearConnectionTimer(): void {
    if (this.connectionTimer) { clearTimeout(this.connectionTimer); this.connectionTimer = null; }
  }

  private cleanup(): void {
    if (this.ws) {
      this.ws.removeAllListeners();
      if (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING) {
        this.ws.close();
      }
      this.ws = null;
    }
  }

  private setState(state: ConnectionState): void { this.state = state; }

  private emit<K extends keyof ClientEvents>(event: K, ...args: Parameters<ClientEvents[K]>): void {
    const handler = this.eventHandlers[event];
    if (handler) (handler as (...a: unknown[]) => void)(...args);
  }
}
