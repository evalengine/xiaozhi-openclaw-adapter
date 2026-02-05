# Contributing to xiaozhi-esp32-adapter

感谢您对 xiaozhi-esp32 OpenClaw 适配器的贡献！

## 开发环境设置

### 系统要求

- Python >= 3.8
- pip
- Git

### 克隆仓库

```bash
git clone https://github.com/openclaw/xiaozhi-esp32-adapter.git
cd xiaozhi-esp32-adapter
```

### 安装开发依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# 安装包（开发模式）
pip install -e ".[test]"
```

## 项目结构

```
xiaozhi-esp32-adapter/
├── xiaozhi_openclaw/           # 主包
│   ├── __init__.py
│   ├── config.py               # 配置加载器
│   ├── protocol.py             # JSON-RPC 2.0 协议
│   ├── tool_executor.py        # 工具执行器
│   ├── websocket_server.py      # WebSocket 服务器
│   ├── executor.py              # 统一工具管理器执行器
│   ├── tools/                  # 工具包装器
│   │   ├── send_message.py
│   │   ├── device_control.py
│   │   └── agent_task.py
│   └── tests/                  # 测试
│       ├── test_protocol.py
│       ├── test_config.py
│       └── test_tool_executor.py
├── tests/                       # 额外测试（如需要）
├── setup.py                     # 包配置
├── pyproject.toml               # 现代 Python 项目配置
└── README.md
```

## 运行测试

```bash
# 运行所有测试
pytest

# 运行带覆盖率的测试
pytest --cov=xiaozhi_openclaw --cov-report=html

# 运行特定测试文件
pytest tests/test_protocol.py

# 详细输出
pytest -v

# 显示打印输出
pytest -s
```

## 代码风格

- 遵循 PEP 8 编码规范
- 使用有意义的变量和函数名
- 添加文档字符串（docstrings）
- 保持代码简洁易读

## 提交代码

### 分支策略

- `main` - 稳定版本
- `develop` - 开发分支

### 提交规范

```
feat: 添加新功能
fix: 修复 bug
docs: 文档更新
test: 添加/更新测试
refactor: 重构代码
chore: 构建/工具链更新
```

### Pull Request 流程

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### PR 要求

- 所有测试必须通过
- 代码覆盖率不应降低
- 需要更新相关文档
- PR 描述需清楚说明更改内容和原因

## 构建

```bash
# 构建 source distribution
python -m build

# 构建 wheel
pip install wheel
python -m wheel --no-deps --build-dir .
```

## 发布

发布由维护者通过 GitHub Actions 自动完成：

1. 合并 PR 到 `main` 分支
2. GitHub Actions 自动运行 CI
3. CI 通过后自动发布到 PyPI

## 报告问题

请在 [GitHub Issues](https://github.com/openclaw/xiaozhi-esp32-adapter/issues) 中报告问题。

请包含：

- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（Python 版本、操作系统等）
- 相关日志

## 行为准则

- 尊重所有贡献者
- 使用友好和包容的语言
- 接受建设性批评
- 关注对社区最有利的事情

## 许可证

通过贡献代码，您同意您的贡献将根据项目的 [MIT 许可证](LICENSE) 进行许可。
