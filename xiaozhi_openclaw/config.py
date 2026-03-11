"""OpenClaw适配器配置加载器"""

import json
import os
from typing import Dict, Any, Optional
from config.config_loader import get_project_dir
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()


class OpenClawConfig:
    """OpenClaw适配器配置"""

    def __init__(self):
        """初始化配置"""
        self.config_path = get_project_dir() + "data/.openclaw_adapter_settings.json"
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            logger.bind(tag=TAG).warning(
                f"OpenClaw配置文件不存在: {self.config_path}，使用默认配置"
            )
            self._config = self._default_config()
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._config = json.load(f)
            logger.bind(tag=TAG).info(f"已加载OpenClaw配置: {self.config_path}")
        except Exception as e:
            logger.bind(tag=TAG).error(f"加载OpenClaw配置失败: {e}，使用默认配置")
            self._config = self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "websocketServer": {
                "enabled": True,
                "host": "0.0.0.0",
                "port": 8080,
                "authToken": None,
            },
            "xiaozhi": {
                "httpPort": 8003,
            },
        }

    def save_config(self) -> None:
        """保存配置到文件"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            logger.bind(tag=TAG).info(f"已保存OpenClaw配置: {self.config_path}")
        except Exception as e:
            logger.bind(tag=TAG).error(f"保存OpenClaw配置失败: {e}")

    @property
    def enabled(self) -> bool:
        """是否启用OpenClaw适配器"""
        return self._config.get("websocketServer", {}).get("enabled", True)

    @property
    def host(self) -> str:
        """WebSocket服务器监听地址"""
        return self._config.get("websocketServer", {}).get("host", "0.0.0.0")

    @property
    def port(self) -> int:
        """WebSocket服务器监听端口"""
        return self._config.get("websocketServer", {}).get("port", 8080)

    @property
    def auth_token(self) -> Optional[str]:
        """认证令牌"""
        return self._config.get("websocketServer", {}).get("authToken")

    @property
    def http_port(self) -> int:
        """小智HTTP服务器端口（用于chat API调用）"""
        return self._config.get("xiaozhi", {}).get("httpPort", 8003)

    def reload(self) -> None:
        """重新加载配置"""
        self._load_config()


# 全局配置实例
_openclaw_config: Optional[OpenClawConfig] = None


def get_openclaw_config() -> OpenClawConfig:
    """获取OpenClaw配置单例"""
    global _openclaw_config
    if _openclaw_config is None:
        _openclaw_config = OpenClawConfig()
    return _openclaw_config
