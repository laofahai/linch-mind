#!/usr/bin/env python3
"""测试连接器发现机制"""

import json
import socket
import struct
import sys


def send_ipc_request(request_data):
    """发送IPC请求到daemon"""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect("/Users/laofahai/.linch-mind/development/daemon.socket")

        # 发送请求
        request_json = json.dumps(request_data)
        request_bytes = request_json.encode("utf-8")
        length_bytes = struct.pack("I", len(request_bytes))
        sock.send(length_bytes + request_bytes)

        # 接收响应
        length_data = sock.recv(4)
        if len(length_data) != 4:
            raise Exception("Failed to read response length")

        response_length = struct.unpack("I", length_data)[0]
        response_bytes = b""
        while len(response_bytes) < response_length:
            chunk = sock.recv(response_length - len(response_bytes))
            if not chunk:
                break
            response_bytes += chunk

        return json.loads(response_bytes.decode("utf-8"))
    finally:
        sock.close()


def main():
    """测试连接器发现"""
    try:
        # 测试连接器列表
        print("=== 测试连接器发现机制 ===")
        result = send_ipc_request({"method": "list_connectors", "params": {}})
        print(f"连接器发现结果:")
        print(json.dumps(result, indent=2))

        # 检查连接器数量
        if "result" in result and isinstance(result["result"], list):
            connector_count = len(result["result"])
            print(f"\n发现 {connector_count} 个连接器")
            if connector_count == 0:
                print("⚠️  未发现任何连接器，可能需要注册")

    except Exception as e:
        print(f"连接器发现测试失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
