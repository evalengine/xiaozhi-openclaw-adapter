/**
 * @evalengine/xiaozhi — OpenClaw plugin for xiaozhi (小智) ESP32 server
 *
 * Provides bidirectional communication between OpenClaw agents and xiaozhi-esp32-server:
 * - xiaozhi_send_message: Send messages to external channels via xiaozhi
 * - xiaozhi_device_control: Control IoT devices connected to xiaozhi
 * - xiaozhi_agent_task: Execute/query agent tasks on xiaozhi
 *
 * Configuration (in ~/.openclaw/config.yaml):
 *   plugins:
 *     xiaozhi:
 *       enabled: true
 *       config:
 *         serverUrl: ws://your-xiaozhi-server:8080/ws
 *         authToken: optional-token
 */

import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { startPlugin, stopPlugin } from "./runtime.js";

export default function register(api: OpenClawPluginApi) {
  api.on("gateway_start", async () => { await startPlugin(api); });
  api.on("gateway_stop", async () => { await stopPlugin(api); });

  // Start immediately (non-blocking)
  startPlugin(api).catch((err: Error) => {
    api.logger.warn(`xiaozhi: Initial start warning: ${err.message}`);
  });
}
