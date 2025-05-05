# Uniproxy

**[English]** | [中文](#中文)

## English

### Introduction
Uniproxy is a versatile SOCKS5 proxy forwarding tool designed to help users easily configure and manage multiple proxy servers on local ports. It supports obtaining proxy information via API or direct input, making it flexible for various use cases.

### Key Features
- **Direct Input for SOCKS5 Proxies**: Manually input proxy information in the format of "host:port" or "host:port:username:password".
- **API Support for Multiple Proxies**: Fetch multiple proxy details with a single API request.
- **Flexible Port Configuration**: Configure the starting local port and the number of proxies for forwarding.
- **Multilingual Interface**: Supports Simplified Chinese, Traditional Chinese, English, and more.
- **Chrome Compatibility Solution**: Solves the issue of Chrome browser not supporting SOCKS5 proxies with username/password authentication. With Uniproxy, you can forward such proxies to a local port (e.g., 127.0.0.1:port) for seamless use in Chrome.

### Installation
1. Download the latest version of `Uniproxy_v1.0.exe` from the [releases](https://github.com/tiktokcc0a/Uniproxy/releases) page.
2. Double-click to run the executable file. No additional installation is required.
3. Ensure your system is running Windows 7 or a higher version.

### Usage
1. **Set Proxy Information**:
   - **Direct Input**: Enter SOCKS5 proxy details in the format "host:port" or "host:port:username:password".
   - **API Link**: Provide an API link to fetch proxy information. For multiple proxies, ensure the link includes a parameter like "num" (e.g., "api_link?num=5").
2. **Configure Ports**: Set the starting port (e.g., 45000) and the number of proxies (e.g., 5).
3. **Start Proxy**: Click "Start Proxy" to launch local SOCKS5 servers and forward to upstream proxies.
4. **Use Proxy**: Configure your browser or application to use a SOCKS5 proxy at "127.0.0.1:starting_port".

For detailed instructions, refer to the [Usage Guide and FAQ](https://5555.blog/archives/uniproxy) (if available).

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Contributing
Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) (if available) for guidelines on how to contribute to this project.

### Contact
For any questions or suggestions, please submit an [Issue](https://github.com/tiktokcc0a/Uniproxy/issues) on GitHub.

---

## 中文

### 介绍
Uniproxy 是一款通用的 SOCKS5 代理转发工具，旨在帮助用户轻松配置和管理本地端口上的多个代理服务器。它支持通过 API 获取代理信息或直接输入，灵活适用于各种用例。

### 主要功能
- **直接输入 SOCKS5 代理信息**：支持以“主机:端口”或“主机:端口:用户名:密码”格式手动输入代理信息。
- **通过 API 获取多个代理**：可通过单个 API 请求获取多个代理信息。
- **灵活的端口配置**：可配置本地起始端口和代理数量，实现灵活转发。
- **多语言界面**：支持简体中文、繁体中文、英语等多种语言。
- **解决 Chrome 浏览器兼容性问题**：针对 Chrome 浏览器不支持带用户名/密码认证的 SOCKS5 节点的问题，Uniproxy 可将此类代理转发到本地端口（如 127.0.0.1:端口），从而实现无缝使用。

### 安装步骤
1. 从[发布页面](https://github.com/tiktokcc0a/Uniproxy/releases)下载最新版本的 `Uniproxy_v1.0.exe`。
2. 双击运行可执行文件，无需额外安装。
3. 确保您的系统为 Windows 7 或更高版本。

### 使用方法
1. **设置代理信息**：
   - **直接输入**：以“主机:端口”或“主机:端口:用户名:密码”格式输入 SOCKS5 代理信息。
   - **API 链接**：提供 API 链接以获取代理信息。如果请求多个代理，请确保链接包含类似“num”的参数（例如，“api_link?num=5”）。
2. **配置端口**：设置起始端口（例如 45000）和代理数量（例如 5）。
3. **启动代理**：点击“启动代理”启动本地 SOCKS5 服务器，并转发到上游代理。
4. **使用代理**：配置您的浏览器或应用程序，使其在“127.0.0.1:starting_port”处使用 SOCKS5 代理。

详细说明请参阅[使用教程及常见问题解答](https://5555.blog/archives/uniproxy)（如有）。

### 许可证
本项目采用 MIT 许可证，详细信息请参见 [LICENSE](LICENSE) 文件。

### 贡献
欢迎贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)（如有）以获取有关如何为此项目做出贡献的指南。

### 联系方式
如有任何疑问或建议，请在 GitHub 上提交 [Issue](https://github.com/tiktokcc0a/Uniproxy/issues)。
