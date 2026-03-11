import { Type } from "@sinclair/typebox";
export const xiaozhiAgentTaskTool = (client, api) => ({
    name: "xiaozhi_agent_task",
    description: "Execute or query agent tasks on the xiaozhi server (execute a task, check status, or cancel a task)",
    parameters: Type.Object({
        action: Type.Unsafe({
            type: "string", enum: ["execute", "status", "cancel"],
            description: "Action to perform",
        }),
        taskId: Type.Optional(Type.String({ description: "Task ID (required for status and cancel actions)" })),
        prompt: Type.Optional(Type.String({ description: "Task prompt/instruction (required for execute action)" })),
        device_id: Type.Optional(Type.String({ description: "Target xiaozhi device MAC address for task execution" })),
    }),
    async execute(_id, params) {
        if (!client.isConnected()) {
            return { content: [{ type: "text", text: "xiaozhi 服务器当前未连接，请检查服务器是否运行。" }], isError: true };
        }
        const { action, taskId, prompt, device_id } = params;
        if (!action)
            throw new Error("Action is required");
        if ((action === "status" || action === "cancel") && !taskId)
            throw new Error(`taskId is required for ${action}`);
        if (action === "execute" && !prompt)
            throw new Error("prompt is required for execute");
        api.logger.info(`xiaozhi_agent_task: action=${action}, taskId=${taskId ?? "N/A"}`);
        const args = { action };
        if (taskId)
            args.taskId = taskId;
        if (prompt)
            args.prompt = prompt;
        if (device_id)
            args.device_id = device_id;
        const result = await client.callTool("xiaozhi_agent_task", args);
        return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }], details: result };
    },
});
