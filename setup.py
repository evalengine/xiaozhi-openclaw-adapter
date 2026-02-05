"""
xiaozhi-esp32 OpenClaw Adapter

A WebSocket server adapter for xiaozhi-esp32-server to integrate with OpenClaw.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="xiaozhi-esp32-adapter",
    version="1.0.0",
    author="OpenClaw Contributors",
    author_email="openclaw@github.com",
    description="OpenClaw adapter for xiaozhi-esp32-server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/openclaw/xiaozhi-esp32-adapter",
    project_urls={
        "Bug Tracker": "https://github.com/openclaw/xiaozhi-esp32-adapter/issues",
        "Source Code": "https://github.com/openclaw/xiaozhi-esp32-adapter",
    },
    packages=find_packages(),
    package_data={
        "xiaozhi_openclaw": ["py.typed"],
    },
    python_requires=">=3.8",
    install_requires=[
        "websockets>=12.0",
    ],
    extras_require={
        "test": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    license="MIT",
    keywords=[
        "xiaozhi",
        "esp32",
        "openclaw",
        "websocket",
        "iot",
        "smart-home",
        "ai-assistant",
    ],
)
