import { z } from "zod";
export declare const XiaozhiPluginConfigSchema: z.ZodObject<{
    serverUrl: z.ZodString;
    authToken: z.ZodOptional<z.ZodString>;
    reconnectInterval: z.ZodDefault<z.ZodNumber>;
    maxReconnectAttempts: z.ZodDefault<z.ZodNumber>;
    heartbeatInterval: z.ZodDefault<z.ZodNumber>;
    connectionTimeout: z.ZodDefault<z.ZodNumber>;
}, z.core.$strict>;
export type XiaozhiPluginConfigInput = z.input<typeof XiaozhiPluginConfigSchema>;
export type XiaozhiPluginConfigOutput = z.output<typeof XiaozhiPluginConfigSchema>;
//# sourceMappingURL=schema.d.ts.map