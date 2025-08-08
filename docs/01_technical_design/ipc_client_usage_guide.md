# IPC客户端使用指南

**版本**: 1.0  
**状态**: 已实现  
**创建时间**: 2025-08-08  
**适用于**: 纯IPC架构客户端集成

## 1. Python IPC客户端示例

### 1.1 基础连接和请求

```python
import asyncio
import json
import struct
from pathlib import Path
import socket

class LinchMindIPCClient:
    """Linch Mind IPC客户端"""
    
    def __init__(self, socket_path: str = None):
        """初始化IPC客户端
        
        Args:
            socket_path: Unix socket路径，默认为 ~/.linch-mind/daemon.sock
        """
        if socket_path is None:
            socket_path = str(Path.home() / ".linch-mind" / "daemon.sock")
        self.socket_path = socket_path
        self.sock = None
    
    async def connect(self):
        """连接到IPC服务器"""
        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.connect(self.socket_path)
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False
    
    async def send_request(self, method: str, path: str, data=None, query_params=None):
        """发送IPC请求
        
        Args:
            method: 请求方法 (GET, POST, PUT, DELETE)
            path: 请求路径
            data: 请求数据
            query_params: 查询参数
            
        Returns:
            响应数据字典
        """
        if not self.sock:
            raise Exception("未连接到服务器")
        
        # 构建IPC请求消息
        request = {
            "method": method,
            "path": path,
            "data": data or {},
            "headers": {"Content-Type": "application/json"},
            "query_params": query_params or {}
        }
        
        # 序列化消息
        message = json.dumps(request).encode('utf-8')
        message_length = struct.pack('>I', len(message))
        
        # 发送消息
        self.sock.sendall(message_length + message)
        
        # 接收响应
        length_data = self.sock.recv(4)
        if len(length_data) != 4:
            raise Exception("接收响应长度失败")
        
        response_length = struct.unpack('>I', length_data)[0]
        response_data = b''
        while len(response_data) < response_length:
            chunk = self.sock.recv(response_length - len(response_data))
            if not chunk:
                break
            response_data += chunk
        
        return json.loads(response_data.decode('utf-8'))
    
    def close(self):
        """关闭连接"""
        if self.sock:
            self.sock.close()
            self.sock = None

# 使用示例
async def main():
    client = LinchMindIPCClient()
    
    if await client.connect():
        try:
            # 获取实体列表
            response = await client.send_request("GET", "/api/v1/entities")
            print("实体列表:", response)
            
            # 获取推荐列表
            response = await client.send_request(
                "GET", 
                "/api/v1/recommendations",
                query_params={"limit": 5}
            )
            print("推荐列表:", response)
            
            # 获取连接器状态
            response = await client.send_request("GET", "/api/v1/connectors")
            print("连接器状态:", response)
            
        finally:
            client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## 2. Flutter/Dart IPC客户端示例

### 2.1 IPC适配器实现

```dart
// lib/services/ipc_client.dart
import 'dart:io';
import 'dart:convert';
import 'dart:typed_data';

class LinchMindIPCClient {
  Socket? _socket;
  final String _socketPath;
  
  LinchMindIPCClient({String? socketPath})
      : _socketPath = socketPath ?? '${Platform.environment['HOME']}/.linch-mind/daemon.sock';
  
  Future<bool> connect() async {
    try {
      _socket = await Socket.connect(
        InternetAddress(_socketPath, type: InternetAddressType.unix),
        0,
      );
      return true;
    } catch (e) {
      print('IPC连接失败: $e');
      return false;
    }
  }
  
  Future<Map<String, dynamic>> sendRequest(
    String method,
    String path, {
    Map<String, dynamic>? data,
    Map<String, dynamic>? queryParams,
  }) async {
    if (_socket == null) {
      throw Exception('未连接到IPC服务器');
    }
    
    // 构建请求消息
    final request = {
      'method': method,
      'path': path,
      'data': data ?? {},
      'headers': {'Content-Type': 'application/json'},
      'query_params': queryParams ?? {},
    };
    
    // 序列化并发送
    final messageBytes = utf8.encode(json.encode(request));
    final lengthBytes = Uint8List(4);
    ByteData.view(lengthBytes.buffer).setUint32(0, messageBytes.length, Endian.big);
    
    _socket!.add(lengthBytes);
    _socket!.add(messageBytes);
    
    // 接收响应
    final responseLength = await _readLength();
    final responseData = await _readData(responseLength);
    
    return json.decode(utf8.decode(responseData));
  }
  
  Future<int> _readLength() async {
    final lengthBytes = await _readExactly(4);
    return ByteData.view(lengthBytes.buffer).getUint32(0, Endian.big);
  }
  
  Future<Uint8List> _readData(int length) async {
    return await _readExactly(length);
  }
  
  Future<Uint8List> _readExactly(int length) async {
    final buffer = <int>[];
    await for (final chunk in _socket!) {
      buffer.addAll(chunk);
      if (buffer.length >= length) {
        return Uint8List.fromList(buffer.take(length).toList());
      }
    }
    throw Exception('连接意外关闭');
  }
  
  void close() {
    _socket?.close();
    _socket = null;
  }
}

// 使用示例
class EntityService {
  final LinchMindIPCClient _client = LinchMindIPCClient();
  
  Future<List<Entity>> getEntities({
    String? type,
    int limit = 50,
    int offset = 0,
  }) async {
    if (!await _client.connect()) {
      throw Exception('无法连接到IPC服务器');
    }
    
    try {
      final response = await _client.sendRequest(
        'GET',
        '/api/v1/entities',
        queryParams: {
          if (type != null) 'type': type,
          'limit': limit,
          'offset': offset,
        },
      );
      
      if (response['status_code'] == 200) {
        final List<dynamic> entities = response['data'] ?? [];
        return entities.map((json) => Entity.fromJson(json)).toList();
      } else {
        throw Exception('获取实体列表失败: ${response['data']}');
      }
    } finally {
      _client.close();
    }
  }
  
  Future<List<Recommendation>> getRecommendations({
    int limit = 10,
    double minScore = 0.0,
  }) async {
    if (!await _client.connect()) {
      throw Exception('无法连接到IPC服务器');
    }
    
    try {
      final response = await _client.sendRequest(
        'GET',
        '/api/v1/recommendations',
        queryParams: {
          'limit': limit,
          'min_score': minScore,
        },
      );
      
      if (response['status_code'] == 200) {
        final List<dynamic> recommendations = response['data'] ?? [];
        return recommendations.map((json) => Recommendation.fromJson(json)).toList();
      } else {
        throw Exception('获取推荐列表失败');
      }
    } finally {
      _client.close();
    }
  }
}
```

## 3. 错误处理和重连机制

### 3.1 自动重连客户端

```python
import asyncio
import logging
from typing import Optional

class ResilientIPCClient(LinchMindIPCClient):
    """带自动重连的IPC客户端"""
    
    def __init__(self, socket_path: str = None, max_retries: int = 3, retry_delay: float = 1.0):
        super().__init__(socket_path)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(__name__)
    
    async def send_request_with_retry(self, method: str, path: str, data=None, query_params=None):
        """带重试的请求发送"""
        for attempt in range(self.max_retries):
            try:
                if not self.sock:
                    if not await self.connect():
                        raise Exception("无法连接到服务器")
                
                return await self.send_request(method, path, data, query_params)
                
            except Exception as e:
                self.logger.warning(f"IPC请求失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                
                # 关闭当前连接
                self.close()
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    raise e

# 使用示例
async def robust_client_example():
    client = ResilientIPCClient(max_retries=3, retry_delay=1.0)
    
    try:
        # 即使连接暂时断开，也会自动重试
        entities = await client.send_request_with_retry("GET", "/api/v1/entities")
        print(f"获取到 {len(entities.get('data', []))} 个实体")
        
    except Exception as e:
        print(f"最终失败: {e}")
    finally:
        client.close()
```

## 4. 性能优化建议

### 4.1 连接池管理

```python
import asyncio
from asyncio import Queue
from contextlib import asynccontextmanager

class IPCConnectionPool:
    """IPC连接池"""
    
    def __init__(self, socket_path: str, max_connections: int = 10):
        self.socket_path = socket_path
        self.max_connections = max_connections
        self._pool = Queue(maxsize=max_connections)
        self._created_connections = 0
    
    async def _create_connection(self) -> LinchMindIPCClient:
        """创建新连接"""
        client = LinchMindIPCClient(self.socket_path)
        if await client.connect():
            return client
        raise Exception("无法创建IPC连接")
    
    @asynccontextmanager
    async def get_connection(self):
        """获取连接（上下文管理器）"""
        try:
            # 尝试从池中获取连接
            client = self._pool.get_nowait()
        except:
            # 如果池为空且未达到最大连接数，创建新连接
            if self._created_connections < self.max_connections:
                client = await self._create_connection()
                self._created_connections += 1
            else:
                # 等待可用连接
                client = await self._pool.get()
        
        try:
            yield client
        finally:
            # 连接使用完后归还到池中
            try:
                self._pool.put_nowait(client)
            except:
                # 池已满，关闭连接
                client.close()
                self._created_connections -= 1

# 使用示例
pool = IPCConnectionPool("/tmp/daemon.sock", max_connections=5)

async def batch_requests():
    """批量请求示例"""
    tasks = []
    
    for i in range(20):  # 20个并发请求
        async def make_request(req_id):
            async with pool.get_connection() as client:
                return await client.send_request("GET", f"/api/v1/entities/{req_id}")
        
        tasks.append(make_request(f"entity_{i:03d}"))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

## 5. 跨平台适配

### 5.1 Windows Named Pipe支持

```python
import platform

class CrossPlatformIPCClient:
    """跨平台IPC客户端"""
    
    def __init__(self, socket_path: str = None, pipe_name: str = None):
        if platform.system() == "Windows":
            self.pipe_name = pipe_name or r"\\.\pipe\linch_mind_daemon"
            self.is_windows = True
        else:
            self.socket_path = socket_path or str(Path.home() / ".linch-mind" / "daemon.sock")
            self.is_windows = False
    
    async def connect(self):
        """跨平台连接"""
        try:
            if self.is_windows:
                # Windows Named Pipe连接
                import win32file
                self.handle = win32file.CreateFile(
                    self.pipe_name,
                    win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                    0, None,
                    win32file.OPEN_EXISTING,
                    0, None
                )
            else:
                # Unix Socket连接
                self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.sock.connect(self.socket_path)
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False
    
    async def send_request(self, method: str, path: str, data=None, query_params=None):
        """跨平台请求发送"""
        request = {
            "method": method,
            "path": path,
            "data": data or {},
            "query_params": query_params or {}
        }
        
        message = json.dumps(request).encode('utf-8')
        message_length = struct.pack('>I', len(message))
        
        if self.is_windows:
            # Windows Named Pipe I/O
            import win32file
            win32file.WriteFile(self.handle, message_length + message)
            
            _, length_data = win32file.ReadFile(self.handle, 4)
            response_length = struct.unpack('>I', length_data)[0]
            
            _, response_data = win32file.ReadFile(self.handle, response_length)
        else:
            # Unix Socket I/O
            self.sock.sendall(message_length + message)
            
            length_data = self.sock.recv(4)
            response_length = struct.unpack('>I', length_data)[0]
            
            response_data = b''
            while len(response_data) < response_length:
                chunk = self.sock.recv(response_length - len(response_data))
                response_data += chunk
        
        return json.loads(response_data.decode('utf-8'))
```

## 6. 调试和监控

### 6.1 带日志的调试客户端

```python
import logging
import time
from typing import Dict, Any

class DebuggingIPCClient(LinchMindIPCClient):
    """带调试功能的IPC客户端"""
    
    def __init__(self, socket_path: str = None, log_level=logging.INFO):
        super().__init__(socket_path)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    async def send_request(self, method: str, path: str, data=None, query_params=None) -> Dict[str, Any]:
        """带性能监控的请求发送"""
        start_time = time.time()
        request_id = f"{method}_{path}_{int(start_time * 1000)}"
        
        self.logger.info(f"[{request_id}] 发送请求: {method} {path}")
        if query_params:
            self.logger.debug(f"[{request_id}] 查询参数: {query_params}")
        if data:
            self.logger.debug(f"[{request_id}] 请求数据: {data}")
        
        try:
            response = await super().send_request(method, path, data, query_params)
            
            elapsed_time = (time.time() - start_time) * 1000  # 转换为毫秒
            status_code = response.get('status_code', 'unknown')
            
            self.logger.info(
                f"[{request_id}] 响应完成: {status_code} "
                f"(用时: {elapsed_time:.2f}ms)"
            )
            
            if elapsed_time > 100:  # 超过100ms警告
                self.logger.warning(f"[{request_id}] 请求耗时过长: {elapsed_time:.2f}ms")
            
            return response
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            self.logger.error(
                f"[{request_id}] 请求失败: {e} "
                f"(用时: {elapsed_time:.2f}ms)"
            )
            raise e
```

---

**总结**: 这个指南提供了完整的IPC客户端实现示例，包括Python和Dart版本，以及错误处理、连接池、跨平台支持和调试功能。开发者可以基于这些示例快速集成Linch Mind的IPC服务。