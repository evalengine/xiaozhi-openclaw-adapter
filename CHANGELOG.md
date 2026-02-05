# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-02-04

### Added
- Initial release of xiaozhi-esp32 OpenClaw adapter
- WebSocket server for receiving OpenClaw plugin connections
- JSON-RPC 2.0 protocol implementation
- Three tool wrappers: send_message, device_control, agent_task
- Unified tool manager integration
- Bearer token authentication support
- Configuration file loader with hot-reload support
- Comprehensive unit tests (49 tests)

### Features
- Async WebSocket server using websockets library
- Tool executor with async support
- Integration with xiaozhi's existing tool system
- Graceful connection handling and cleanup
- Detailed logging for debugging

### Configuration
- `enabled`: Enable/disable WebSocket server (default: true)
- `host`: Listen address (default: "0.0.0.0")
- `port`: Listen port (default: 8080)
- `authToken`: Optional authentication token

### Dependencies
- websockets >= 12.0

[1.0.0]: https://github.com/openclaw/xiaozhi-esp32-adapter/releases/tag/v1.0.0
