#!/usr/bin/env python3
"""
测试事件API的简单客户端
"""

import json
import socket
import uuid
import time
from pathlib import Path

def send_test_event():
    """发送测试文件事件"""
    
    # 找到daemon socket - 从daemon日志获取
    import subprocess
    result = subprocess.run(['./linch-mind', 'daemon', 'logs'], capture_output=True, text=True, cwd='.')
    
    socket_path = None
    for line in result.stdout.split('\n'):
        if 'Unix Domain Socket 已就绪' in line or 'Unix socket path' in line:
            # 尝试从日志中提取socket路径
            if '/var/folders/' in line:
                import re
                match = re.search(r'/var/folders/[^/]+/[^/]+/T/linch-mind-\d+\.sock', line)
                if match:
                    socket_path = match.group()
                    break
    
    if not socket_path:
        socket_path = "/var/folders/dw/y348mck15dq4z2jjqw65rynm0000gn/T/linch-mind-95529.sock"  # 默认路径
    print(f"🔌 Connecting to daemon socket: {socket_path}")
    
    try:
        # 连接到Unix socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(str(socket_path))
        
        # 认证请求
        auth_request = {
            "method": "POST",
            "path": "/auth/authenticate",
            "data": {},
            "request_id": str(uuid.uuid4())
        }
        
        auth_message = json.dumps(auth_request) + "\n"
        sock.send(auth_message.encode('utf-8'))
        
        # 接收认证响应
        auth_response = sock.recv(4096).decode('utf-8').strip()
        print(f"📝 Auth response: {auth_response[:100]}...")
        
        # 发送文件事件
        event_data = {
            "connector_id": "filesystem",
            "event_type": "created",
            "file_path": "/tmp/test_dir/test_file.txt",
            "timestamp": "2025-08-10T19:45:00Z",
            "metadata": {
                "size": 100,
                "extension": ".txt",
                "directory": "/tmp/test_dir"
            }
        }
        
        event_request = {
            "method": "POST", 
            "path": "/events/file-changed",
            "data": event_data,
            "request_id": str(uuid.uuid4())
        }
        
        event_message = json.dumps(event_request) + "\n"
        print(f"📁 Sending event: {event_data}")
        
        sock.send(event_message.encode('utf-8'))
        
        # 接收事件响应
        event_response = sock.recv(4096).decode('utf-8').strip()
        response_data = json.loads(event_response)
        
        if response_data.get("success"):
            print(f"✅ Event processed successfully: {response_data.get('data', {}).get('message')}")
        else:
            print(f"❌ Event failed: {response_data.get('error', {}).get('message')}")
            
        sock.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    send_test_event()