import asyncio
import socket
import threading
import time
import requests
import socks
from concurrent.futures import ThreadPoolExecutor, as_completed

class ProxyManager:
    def __init__(self):
        # 存储每个端口对应的代理服务器任务和事件循环
        self.port_to_server = {}
        self.port_to_loop = {}
        self.port_to_thread = {}

    class Socks5Server:
        def __init__(self, local_port, upstream_host, upstream_port, username=None, password=None):
            self.local_port = local_port
            self.upstream_host = upstream_host
            self.upstream_port = upstream_port
            self.username = username
            self.password = password
            self.server = None
            self.running = False

        async def handle_client(self, reader, writer):
            client_addr = writer.get_extra_info('peername')
            print(f"客户端连接到端口 {self.local_port}，来自 {client_addr}")
            try:
                data = await reader.read(1024)
                if not data or len(data) < 3 or data[0] != 5:
                    print(f"端口 {self.local_port}：无效的 SOCKS5 握手，数据: {data}")
                    return
                
                writer.write(b'\x05\x00')
                await writer.drain()
                print(f"端口 {self.local_port}：完成 SOCKS5 握手")

                data = await reader.read(1024)
                if len(data) < 4 or data[0] != 5:
                    print(f"端口 {self.local_port}：无效的 SOCKS5 请求，数据: {data}")
                    return

                cmd = data[1]
                if cmd != 1:
                    writer.write(b'\x05\x07\x00\x01\x00\x00\x00\x00\x00\x00')
                    await writer.drain()
                    print(f"端口 {self.local_port}：不支持的命令 {cmd}")
                    return

                addr_type = data[3]
                if addr_type == 1:
                    if len(data) < 10:
                        print(f"端口 {self.local_port}：IPv4 数据长度不足，数据: {data}")
                        return
                    target_ip = socket.inet_ntoa(data[4:8])
                    target_port = int.from_bytes(data[8:10], 'big')
                elif addr_type == 3:
                    domain_len = data[4]
                    if len(data) < 5 + domain_len + 2:
                        print(f"端口 {self.local_port}：域名数据长度不足，数据: {data}")
                        return
                    target_ip = data[5:5 + domain_len].decode('utf-8')
                    target_port = int.from_bytes(data[5 + domain_len:5 + domain_len + 2], 'big')
                else:
                    writer.write(b'\x05\x08\x00\x01\x00\x00\x00\x00\x00\x00')
                    await writer.drain()
                    print(f"端口 {self.local_port}：不支持的地址类型 {addr_type}")
                    return

                print(f"端口 {self.local_port}：连接目标 {target_ip}:{target_port}")

                try:
                    upstream_sock = socks.socksocket()
                    upstream_sock.set_proxy(
                        socks.SOCKS5,
                        self.upstream_host,
                        self.upstream_port,
                        username=self.username if self.username else "",
                        password=self.password if self.password else ""
                    )
                    upstream_sock.connect((target_ip, target_port))
                    print(f"端口 {self.local_port}：成功连接上游服务器 {self.upstream_host}:{self.upstream_port}")
                except Exception as e:
                    writer.write(b'\x05\x05\x00\x01\x00\x00\x00\x00\x00\x00')
                    await writer.drain()
                    print(f"端口 {self.local_port}：连接上游服务器失败: {e}")
                    return

                writer.write(b'\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00')
                await writer.drain()
                print(f"端口 {self.local_port}：通知客户端连接成功")

                upstream_reader, upstream_writer = await asyncio.open_connection(sock=upstream_sock)

                async def forward(reader, writer, direction):
                    try:
                        while True:
                            data = await reader.read(4096)
                            if not data:
                                print(f"端口 {self.local_port}：{direction} 连接关闭")
                                break
                            writer.write(data)
                            await writer.drain()
                    except Exception as e:
                        print(f"端口 {self.local_port}：{direction} 转发异常: {e}")

                tasks = [
                    forward(reader, upstream_writer, "客户端->上游"),
                    forward(upstream_reader, writer, "上游->客户端")
                ]
                await asyncio.gather(*tasks)

            except Exception as e:
                print(f"处理客户端连接时出错（端口 {self.local_port}）：{e}")
            finally:
                writer.close()
                await writer.wait_closed()
                print(f"端口 {self.local_port}：客户端连接关闭")

        async def start(self):
            try:
                self.server = await asyncio.start_server(
                    self.handle_client, '0.0.0.0', self.local_port
                )
                self.running = True
                print(f"SOCKS5 服务器启动在端口 {self.local_port}")
                async with self.server:
                    await self.server.serve_forever()
            except Exception as e:
                print(f"启动 SOCKS5 服务器时出错（端口 {self.local_port}）：{e}")
                self.running = False

        async def stop(self):
            if self.server and self.running:
                self.running = False
                self.server.close()
                await self.server.wait_closed()
                print(f"SOCKS5 服务器停止在端口 {self.local_port}")

    def stop_proxy_on_port(self, port):
        """停止指定端口的代理服务器"""
        if port in self.port_to_server:
            server = self.port_to_server[port]
            loop = self.port_to_loop[port]
            thread = self.port_to_thread[port]
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(server.stop(), loop)
                try:
                    future.result(timeout=2.0)
                except asyncio.TimeoutError:
                    print(f"停止端口 {port} 的服务器超时")
            loop.call_soon_threadsafe(loop.stop)
            thread.join(timeout=3.0)
            if thread.is_alive():
                print(f"线程在端口 {port} 未正常终止")
            del self.port_to_server[port]
            del self.port_to_loop[port]
            del self.port_to_thread[port]
            time.sleep(0.5)
            print(f"已停止端口 {port} 的代理服务器")

    def start_proxy_for_port(self, port, upstream_host, upstream_port, username=None, password=None, retries=3, retry_delay=1):
        """为指定端口启动 SOCKS5 代理服务器，带有重试机制"""
        self.stop_proxy_on_port(port)
        for attempt in range(retries):
            try:
                server = self.Socks5Server(port, upstream_host, upstream_port, username, password)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.create_task(server.start())
                thread = threading.Thread(target=loop.run_forever, daemon=True)
                thread.start()
                self.port_to_server[port] = server
                self.port_to_loop[port] = loop
                self.port_to_thread[port] = thread
                return True
            except Exception as e:
                print(f"尝试 {attempt+1}/{retries} 启动端口 {port} 失败: {e}")
                if attempt < retries - 1:
                    time.sleep(retry_delay)
                continue
        print(f"无法在端口 {port} 上启动代理服务器，已重试 {retries} 次")
        return False

    def parse_proxy_info(self, proxy_input):
        """解析用户输入的 SOCKS5 代理信息"""
        parts = proxy_input.strip().split(':')
        if len(parts) < 2:
            raise ValueError("代理信息格式错误，至少需要 host:port")
        
        host = parts[0]
        port = int(parts[1])
        username = None
        password = None
        
        if len(parts) == 4:
            username = parts[2]
            password = parts[3]
        elif len(parts) > 2 and len(parts) != 4:
            raise ValueError("代理信息格式错误，应该是 host:port 或 host:port:username:password")
        
        return host, port, username, password

    def fetch_proxy_from_api(self, api_link, retries=2, retry_delay=2):
        """从 API 链接获取代理信息，支持重试机制"""
        for attempt in range(retries):
            try:
                print(f"正在请求 API 获取代理信息: {api_link} (尝试 {attempt+1}/{retries})")
                response = requests.get(api_link, timeout=30)
                response.raise_for_status()
                content_type = response.headers.get('Content-Type', '').lower()
                text = response.text.strip()

                print(f"API 响应内容: {text[:200]}... (截断)")

                if 'json' in content_type or text.startswith('{') or text.startswith('['):
                    data = response.json()
                    # 检查返回数据是否有效
                    if data.get("success") is False or data.get("data") is None:
                        error_msg = data.get("msg", "API 返回数据无效")
                        raise ValueError(f"API 返回错误: {error_msg}")
                    
                    # 如果是批量请求，data 可能是列表
                    if isinstance(data.get("data"), list):
                        proxies = []
                        for item in data["data"]:
                            host = item.get('host') or item.get('ip') or item.get('server')
                            port = item.get('port')
                            username = item.get('username') or item.get('user')
                            password = item.get('password') or item.get('pass')
                            if host and port:
                                proxies.append((host, int(port), username, password))
                        return proxies
                    else:
                        host = data.get('host') or data.get('ip') or data.get('server')
                        port = data.get('port')
                        username = data.get('username') or data.get('user')
                        password = data.get('password') or data.get('pass')
                        
                        if not host or not port:
                            raise ValueError("API 返回的 JSON 中未找到 host 或 port 字段")
                        return [(host, int(port), username, password)]
                else:
                    lines = text.split('\n')
                    proxies = []
                    for line in lines:
                        if line.strip():
                            try:
                                host, port, username, password = self.parse_proxy_info(line.strip())
                                proxies.append((host, port, username, password))
                            except ValueError as e:
                                print(f"解析文本行失败: {line}, 错误: {e}")
                                continue
                    if proxies:
                        return proxies
                    else:
                        raise ValueError("无法从文本中解析有效的代理信息")

            except requests.exceptions.RequestException as e:
                error_msg = f"从 API 获取代理信息失败，请求异常: {str(e)}"
                print(error_msg)
                if attempt < retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise ValueError(error_msg)
            except Exception as e:
                error_msg = f"从 API 获取代理信息失败，解析错误: {str(e)}"
                print(error_msg)
                if attempt < retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise ValueError(error_msg)

    def start_proxies(self, proxy_input, api_link, start_port, port_count):
        """启动多个代理，支持单次 API 请求获取多个代理信息"""
        success_count = 0
        failed_ports = []

        if api_link:
            try:
                proxies = self.fetch_proxy_from_api(api_link)
                if len(proxies) >= port_count:
                    # 成功获取足够数量的代理
                    print(f"一次性请求成功，获取了 {len(proxies)} 个代理")
                    for i in range(port_count):
                        port = start_port + i
                        upstream_host, upstream_port, username, password = proxies[i]
                        print(f"使用获取的代理信息用于端口 {port}: {upstream_host}:{upstream_port}")
                        if self.start_proxy_for_port(port, upstream_host, upstream_port, username, password):
                            success_count += 1
                        else:
                            failed_ports.append(port)
                else:
                    # 获取数量不足
                    print(f"获取的代理数量不足 ({len(proxies)}/{port_count})")
                    for i in range(min(len(proxies), port_count)):
                        port = start_port + i
                        upstream_host, upstream_port, username, password = proxies[i]
                        print(f"使用获取的代理信息用于端口 {port}: {upstream_host}:{upstream_port}")
                        if self.start_proxy_for_port(port, upstream_host, upstream_port, username, password):
                            success_count += 1
                        else:
                            failed_ports.append(port)
                    for i in range(len(proxies), port_count):
                        failed_ports.append(start_port + i)
            except ValueError as e:
                print(f"从 API 获取代理信息失败: {e}")
                failed_ports.extend(range(start_port, start_port + port_count))
        else:
            try:
                upstream_host, upstream_port, username, password = self.parse_proxy_info(proxy_input)
                print(f"使用直接输入的代理信息: {upstream_host}:{upstream_port}")
                for i in range(port_count):
                    port = start_port + i
                    if self.start_proxy_for_port(port, upstream_host, upstream_port, username, password):
                        success_count += 1
                    else:
                        failed_ports.append(port)
            except ValueError as e:
                raise ValueError(e)

        return success_count, failed_ports

    def stop_all_proxies(self):
        """关闭所有运行的代理服务器"""
        for port in list(self.port_to_server.keys()):
            self.stop_proxy_on_port(port)
