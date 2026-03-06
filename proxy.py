#!/usr/bin/env python3
"""
简单的 HTTP 反向代理 - 将本地端口暴露到公网
"""

import socket
import threading
import sys

def handle_client(client_socket, target_host, target_port):
    """处理客户端连接，转发到目标服务"""
    try:
        # 连接到目标服务
        target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target.connect((target_host, target_port))
        
        # 双向转发
        def forward(source, destination):
            while True:
                try:
                    data = source.recv(4096)
                    if not data:
                        break
                    destination.send(data)
                except:
                    break
            source.close()
            destination.close()
        
        # 启动两个转发线程
        t1 = threading.Thread(target=forward, args=(client_socket, target))
        t2 = threading.Thread(target=forward, args=(target, client_socket))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    except Exception as e:
        print(f"Error: {e}")
        client_socket.close()

def start_proxy(listen_port, target_host, target_port):
    """启动代理服务器"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', listen_port))
    server.listen(5)
    print(f"[*] Proxy listening on 0.0.0.0:{listen_port}")
    print(f"[*] Forwarding to {target_host}:{target_port}")
    
    while True:
        client, addr = server.accept()
        print(f"[*] Connection from {addr[0]}:{addr[1]}")
        handler = threading.Thread(
            target=handle_client, 
            args=(client, target_host, target_port)
        )
        handler.start()

if __name__ == "__main__":
    # 前端代理 - 暴露到 8080 端口
    if len(sys.argv) > 1 and sys.argv[1] == "backend":
        start_proxy(8080, "localhost", 8000)
    else:
        start_proxy(8080, "localhost", 5173)
