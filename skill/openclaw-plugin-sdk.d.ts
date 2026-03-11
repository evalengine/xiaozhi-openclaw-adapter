declare module "openclaw/plugin-sdk" {
  export interface OpenClawPluginLogger {
    info(message: string, ...args: unknown[]): void;
    warn(message: string, ...args: unknown[]): void;
    error(message: string, ...args: unknown[]): void;
    debug(message: string, ...args: unknown[]): void;
  }

  export interface ToolDefinition {
    name: string;
    description: string;
    parameters: unknown;
    execute(id: string, params: Record<string, unknown>): Promise<unknown>;
  }

  export interface OpenClawPluginApi {
    getConfig(): Record<string, unknown>;
    pluginConfig?: Record<string, unknown>;
    getAgentId(): string;
    logger: OpenClawPluginLogger;
    emit(event: string, data?: unknown): void;
    on(event: string, handler: (...args: unknown[]) => void): void;
    registerTool(definition: ToolDefinition): void;
  }

  export interface OpenClawPluginConfig {
    uiHints?: Record<string, {
      label?: string;
      help?: string;
      placeholder?: string;
      sensitive?: boolean;
      advanced?: boolean;
    }>;
  }

  export interface OpenClawPluginDefinition {
    id: string;
    name: string;
    description?: string;
    version?: string;
    configSchema?: OpenClawPluginConfig;
    activate?(api: OpenClawPluginApi): Promise<void> | void;
    deactivate?(api: OpenClawPluginApi): Promise<void> | void;
  }
}
