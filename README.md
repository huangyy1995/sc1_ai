# Distributed StarCraft AI Architecture / 分布式星际争霸AI架构

本项目是一个分布式的《星际争霸：母巢之战》（StarCraft: Brood War）AI 系统架构。该系统将 AI 决策引擎和游戏运行环境物理分离，通过 TCP/IP 协议进行通信。这种设计允许开发者在 Mac、Linux 等非 Windows 环境下进行星际争霸 AI 的开发和运算（尤其是深度学习相关的运算），同时在 Windows 上运行依赖于 BWAPI 的游戏环境。

## 架构说明

系统分为两个主要节点：

- **Windows 执行节点 (Bridge / Server)**: 
  位于 `windows_bridge` 目录下。该节点负责实际运行星际争霸游戏。它通过 `pybrood`（BWAPI 的 Python 封装）挂载到游戏中，获取游戏状态信息，并将其序列化后通过 TCP Server（默认端口 `9999`）发送出去；同时，它会堵塞等待接收来自客户端的操作指令，并在游戏中执行该指令。

- **Mac/Linux 决策节点 (Client)**: 
  位于 `mac_client` 目录下。该节点负责 AI 的核心决策逻辑。它作为 TCP Client 连接到 Windows 节点，接收当前游戏帧的状态（如己方单位信息、矿物分布、资源情况等），基于状态进行处理后（现阶段为简单的规则脚本，未来易于集成深度学习/强化学习模型），返回对应的操作指令（如建造农民、采集矿物等）给 Windows 节点执行。

## 目录结构

```text
sc_training/
├── windows_bridge/
│   └── tcp_server_bot.py    # Windows 端 TCP 服务器与 BWAPI 机器人代码
├── mac_client/
│   └── bot_client.py        # Mac 端的 TCP 客户端代码，包含基础 AI 逻辑
└── README.md
```

## 运行环境依赖

### Windows 节点 (游戏运行环境)
- 操作系统: Windows
- Python: 3.x
- 依赖项: 
  - 星际争霸：母巢之战 (StarCraft: Brood War) v1.16.1
  - [BWAPI](https://github.com/bwapi/bwapi)
  - [pybrood](https://github.com/aigamedev/pybrood) (或根据实际绑定的 python BWAPI 库进行调整)

### Mac / Linux 节点 (AI 决策环境)
- 操作系统: macOS / Linux (也可以是另一台 Windows)
- Python: 3.x
- 依赖项: 
  - 仅依赖 Python 标准库 (`socket`, `json`, `time`, `argparse`)
  - 未来可额外引入 `PyTorch`, `TensorFlow` 等机器学习库

## 使用方法

1. **网络配置**: 
   确保 AI 决策端（Mac/Linux）能够连接到游戏运行端（Windows）的 IP 地址。如果在同一台机器上进行测试，可以默认使用 `127.0.0.1`。

2. **启动 Windows 节点**:
   在 Windows 机器上，通过 Chaoslauncher 或其他工具启动注入了 BWAPI 的星际争霸，并运行 Server 端代码。
   ```bash
   python windows_bridge/tcp_server_bot.py
   ```
   启动后，游戏进入第一帧时会在 `9999` 端口堵塞并等待连接。

3. **启动 Mac 节点**:
   在开发机（如 Mac）上运行 Client 端代码，并指定 Windows 机器的 IP 地址（默认为本机 127.0.0.1，端口为 9999）。
   ```bash
   python mac_client/bot_client.py --ip <Windows的IP地址> --port 9999
   ```

## 当前已实现功能
- **TCP 通信桥接**: 稳定地桥接游戏环境与外部异构操作系统的 AI 开发环境。
- **状态同步**: 基础游戏状态的获取与序列化（包括主基地信息、农民状态、水晶矿坐标与数量、人口及资源情况）。
- **基础规则 AI**:
  - 基地有充足水晶且空闲时，自动训练农民。
  - 自动检测并指派空闲的农民采矿。

## 未来的工作
- **功能扩充**: 前往客户端暴露更多 BWAPI 操作指令（如科技研究、建筑建造、军队微操施放等），以支持完整的星际争霸对抗。
- **状态补全**: 提供视野内敌方单位的状态同步。
- **引入深度学习**: 在 `bot_client.py` 端接入强化学习环境和神经网络模型，使架构演进为完整的高级强化学习训练平台。
