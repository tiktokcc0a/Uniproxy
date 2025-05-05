# Uniproxy

Uniproxy is a universal SOCKS5 proxy forwarding tool designed to help users easily configure and manage multiple proxy servers on local ports. It supports fetching proxy information from APIs or direct input, making it flexible for various use cases.

## Features
- Supports direct input of SOCKS5 proxy information.
- Fetches multiple proxy information from a single API request.
- Configurable local ports and proxy count for flexible forwarding.
- Multilingual interface (Simplified Chinese, Traditional Chinese, English, and more).

## Installation
1. Download the latest release of `Uniproxy_v1.0.exe` from the [Releases](https://github.com/tiktokcc0a/Uniproxy/releases) page.
2. Double-click to run the executable. No additional installation is required.
3. Ensure your system is Windows 7 or above.

## Usage
1. **Set Proxy Information**:
   - **Direct Input**: Enter SOCKS5 proxy info in the format `host:port` or `host:port:username:password`.
   - **API Link**: Provide an API link to fetch proxy information. If requesting multiple proxies, ensure the link includes a parameter like `num` (e.g., `api_link?num=5`).
2. **Configure Ports**: Set the starting port (e.g., 45000) and proxy count (e.g., 5).
3. **Start Proxies**: Click 'Start Proxies' to launch local SOCKS5 servers forwarding to upstream proxies.
4. **Use Proxies**: Configure your browser or application to use SOCKS5 proxy at `127.0.0.1:starting_port`.

For detailed instructions, refer to the [Usage Tutorial & FAQ](https://5555.blog/archives/uniproxy) (if hosted).

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing
Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) (if available) for guidelines on how to contribute to this project.

## Contact
For issues or suggestions, please open an [Issue](https://github.com/tiktokcc0a/Uniproxy/issues) on GitHub.
