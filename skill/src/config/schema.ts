import { z } from "zod";

export const XiaozhiPluginConfigSchema = z.object({
  serverUrl: z.string().min(1, "serverUrl is required"),
  authToken: z.string().optional(),
  reconnectInterval: z.number().int().positive().default(5000),
  maxReconnectAttempts: z.number().int().positive().default(10),
  heartbeatInterval: z.number().int().positive().default(30000),
  connectionTimeout: z.number().int().positive().default(10000),
}).strict();

export type XiaozhiPluginConfigInput = z.input<typeof XiaozhiPluginConfigSchema>;
export type XiaozhiPluginConfigOutput = z.output<typeof XiaozhiPluginConfigSchema>;
