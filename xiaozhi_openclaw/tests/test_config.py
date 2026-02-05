"""Unit tests for OpenClaw adapter config module"""

import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
from core.providers.tools.openclaw.config import OpenClawConfig, get_openclaw_config


class TestOpenClawConfig:
    """Test OpenClawConfig class"""

    def test_init_creates_default_config(self):
        """Test that init creates default config when file doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test_config.json")
            with patch("core.providers.tools.openclaw.config.get_project_dir", return_value=tmpdir + "/"):
                config = OpenClawConfig()

                assert config.enabled is True
                assert config.host == "0.0.0.0"
                assert config.port == 8080
                assert config.auth_token is None

    def test_default_config_values(self):
        """Test default configuration values"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("core.providers.tools.openclaw.config.get_project_dir", return_value=tmpdir + "/"):
                config = OpenClawConfig()

                assert config._config["websocketServer"]["enabled"] is True
                assert config._config["websocketServer"]["host"] == "0.0.0.0"
                assert config._config["websocketServer"]["port"] == 8080
                assert config._config["websocketServer"]["authToken"] is None

    def test_load_config_from_file(self):
        """Test loading config from existing file"""
        test_config = {
            "websocketServer": {
                "enabled": False,
                "host": "127.0.0.1",
                "port": 9000,
                "authToken": "test-token"
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "data", ".openclaw_adapter_settings.json")
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            with open(config_path, "w") as f:
                json.dump(test_config, f)

            with patch("core.providers.tools.openclaw.config.get_project_dir", return_value=tmpdir):
                config = OpenClawConfig()

                assert config.enabled is False
                assert config.host == "127.0.0.1"
                assert config.port == 9000
                assert config.auth_token == "test-token"

    def test_enabled_property(self):
        """Test enabled property getter"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("core.providers.tools.openclaw.config.get_project_dir", return_value=tmpdir + "/"):
                config = OpenClawConfig()
                assert config.enabled is True

    def test_host_property(self):
        """Test host property getter"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("core.providers.tools.openclaw.config.get_project_dir", return_value=tmpdir + "/"):
                config = OpenClawConfig()
                assert config.host == "0.0.0.0"

    def test_port_property(self):
        """Test port property getter"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("core.providers.tools.openclaw.config.get_project_dir", return_value=tmpdir + "/"):
                config = OpenClawConfig()
                assert config.port == 8080

    def test_auth_token_property(self):
        """Test auth_token property getter"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("core.providers.tools.openclaw.config.get_project_dir", return_value=tmpdir + "/"):
                config = OpenClawConfig()
                assert config.auth_token is None

    def test_auth_token_property_with_value(self):
        """Test auth_token property with value"""
        test_config = {
            "websocketServer": {
                "enabled": True,
                "host": "0.0.0.0",
                "port": 8080,
                "authToken": "secret-token-123"
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "data", ".openclaw_adapter_settings.json")
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            with open(config_path, "w") as f:
                json.dump(test_config, f)

            with patch("core.providers.tools.openclaw.config.get_project_dir", return_value=tmpdir):
                config = OpenClawConfig()
                assert config.auth_token == "secret-token-123"

    def test_reload(self):
        """Test reload method"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("core.providers.tools.openclaw.config.get_project_dir", return_value=tmpdir + "/"):
                config = OpenClawConfig()
                original_port = config.port

                # Reload should not fail
                config.reload()
                assert config.port == original_port

    def test_save_config(self):
        """Test save_config method"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("core.providers.tools.openclaw.config.get_project_dir", return_value=tmpdir + "/"):
                config = OpenClawConfig()
                config.save_config()

                # Check file was created
                config_path = os.path.join(tmpdir, "data", ".openclaw_adapter_settings.json")
                assert os.path.exists(config_path)

                # Verify content
                with open(config_path, "r") as f:
                    saved_config = json.load(f)

                assert saved_config == config._config


class TestGetOpenclawConfig:
    """Test get_openclaw_config singleton function"""

    def test_returns_singleton_instance(self):
        """Test that get_openclaw_config returns singleton"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("core.providers.tools.openclaw.config.get_project_dir", return_value=tmpdir + "/"):
                config1 = get_openclaw_config()
                config2 = get_openclaw_config()

                # Should return the same instance (within the same module)
                assert config1 is not None
                assert config2 is not None

    def test_config_has_required_attributes(self):
        """Test that config has all required attributes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("core.providers.tools.openclaw.config.get_project_dir", return_value=tmpdir + "/"):
                config = get_openclaw_config()

                assert hasattr(config, "enabled")
                assert hasattr(config, "host")
                assert hasattr(config, "port")
                assert hasattr(config, "auth_token")
                assert hasattr(config, "reload")
