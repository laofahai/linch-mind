#!/usr/bin/env python3
"""
IPC性能基准测试工具
测试延迟、吞吐量、并发处理能力等关键指标
"""

import asyncio
import json
import os
import socket
import statistics
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
import threading

# 添加daemon目录到路径
sys.path.insert(0, str(Path(__file__).parent / "daemon"))

from services.ipc_protocol import IPCRequest, IPCResponse


class IPCPerformanceBenchmark:
    """IPC性能基准测试"""
    
    def __init__(self, socket_path: str):
        self.socket_path = socket_path
        self.results = {}
        
    def _connect_socket(self) -> socket.socket:
        """创建IPC socket连接"""
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.socket_path)
        return sock
    
    def _authenticate_connection(self, sock: socket.socket) -> bool:
        """对连接进行认证握手"""
        try:
            # 发送认证请求 (POST /auth/handshake)
            auth_response, _ = self._send_ipc_message(
                sock, 
                "/auth/handshake",
                {"client_pid": os.getpid()},
                "POST"
            )
            return auth_response.get("success", False)
        except Exception as e:
            print(f"认证失败: {e}")
            return False
        
    def _send_ipc_message(self, sock: socket.socket, path: str, params: Dict[str, Any] = None, http_method: str = "GET") -> Tuple[Dict[str, Any], float]:
        """发送IPC消息并测量延迟"""
        start_time = time.perf_counter()
        
        # 构建请求
        message = IPCRequest(
            method=http_method,
            path=path if path.startswith('/') else f"/{path.replace('.', '/')}",
            data=params or {},
            request_id=f"bench_{threading.get_ident()}_{time.time()}"
        )
        
        # 发送请求
        data = json.dumps(message.to_dict()).encode()
        sock.sendall(len(data).to_bytes(4, 'big'))
        sock.sendall(data)
        
        # 接收响应
        length_bytes = sock.recv(4)
        if not length_bytes:
            raise RuntimeError("Connection closed")
            
        length = int.from_bytes(length_bytes, 'big')
        response_data = sock.recv(length)
        
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        
        response = json.loads(response_data.decode())
        return response, latency_ms
    
    def test_single_request_latency(self, num_requests: int = 100) -> Dict[str, Any]:
        """测试单次请求延迟"""
        print(f"🔍 测试单次请求延迟 (n={num_requests})")
        
        latencies = []
        successful_requests = 0
        errors = []
        
        sock = self._connect_socket()
        
        # 进行认证握手
        if not self._authenticate_connection(sock):
            print("   ❌ 认证失败，无法继续测试")
            sock.close()
            return {"error": "Authentication failed", "errors": ["Authentication failed"]}
        
        try:
            for i in range(num_requests):
                try:
                    response, latency = self._send_ipc_message(sock, "/health")
                    latencies.append(latency)
                    # 调试：打印失败响应内容
                    if not response.get("success", False) and len(errors) < 5:
                        print(f"     失败响应 {i}: {response}")
                    # 检查响应是否成功
                    if response.get("success", False) or response.get("status_code") == 200:
                        successful_requests += 1
                except Exception as e:
                    errors.append(str(e))
                    if len(errors) <= 5:
                        print(f"     异常 {i}: {e}")
                    
        finally:
            sock.close()
        
        if not latencies:
            return {"error": "No successful requests", "errors": errors}
            
        result = {
            "test": "single_request_latency",
            "total_requests": num_requests,
            "successful_requests": successful_requests,
            "error_rate": (num_requests - successful_requests) / num_requests * 100,
            "latency_ms": {
                "min": min(latencies),
                "max": max(latencies),
                "mean": statistics.mean(latencies),
                "median": statistics.median(latencies),
                "p95": statistics.quantiles(latencies, n=20)[18] if len(latencies) > 20 else max(latencies),
                "p99": statistics.quantiles(latencies, n=100)[98] if len(latencies) > 100 else max(latencies),
                "stdev": statistics.stdev(latencies) if len(latencies) > 1 else 0
            },
            "errors": errors[:10]  # 只保留前10个错误
        }
        
        print(f"   平均延迟: {result['latency_ms']['mean']:.2f}ms")
        print(f"   P95延迟: {result['latency_ms']['p95']:.2f}ms")  
        print(f"   P99延迟: {result['latency_ms']['p99']:.2f}ms")
        print(f"   成功率: {successful_requests}/{num_requests} ({successful_requests/num_requests*100:.1f}%)")
        
        return result
    
    def test_concurrent_requests(self, concurrent_clients: int = 10, requests_per_client: int = 50) -> Dict[str, Any]:
        """测试并发请求处理能力"""
        print(f"⚡ 测试并发请求处理 ({concurrent_clients} 并发客户端, 每客户端 {requests_per_client} 请求)")
        
        all_latencies = []
        total_errors = []
        start_time = time.perf_counter()
        
        def worker_thread(client_id: int) -> Tuple[List[float], List[str]]:
            """工作线程函数"""
            latencies = []
            errors = []
            
            try:
                sock = self._connect_socket()
                
                # 进行认证握手
                if not self._authenticate_connection(sock):
                    errors.append(f"Client {client_id}: Authentication failed")
                    return latencies, errors
                
                for i in range(requests_per_client):
                    try:
                        response, latency = self._send_ipc_message(sock, "/health")
                        latencies.append(latency)
                    except Exception as e:
                        errors.append(f"Client {client_id}: {str(e)}")
                        
                sock.close()
                        
            except Exception as e:
                errors.append(f"Client {client_id} connection error: {str(e)}")
                
            return latencies, errors
        
        # 启动并发测试
        with ThreadPoolExecutor(max_workers=concurrent_clients) as executor:
            futures = [executor.submit(worker_thread, i) for i in range(concurrent_clients)]
            
            for future in futures:
                latencies, errors = future.result()
                all_latencies.extend(latencies)
                total_errors.extend(errors)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        total_requests = concurrent_clients * requests_per_client
        successful_requests = len(all_latencies)
        
        if not all_latencies:
            return {"error": "No successful concurrent requests", "errors": total_errors}
        
        result = {
            "test": "concurrent_requests", 
            "concurrent_clients": concurrent_clients,
            "requests_per_client": requests_per_client,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "error_rate": (total_requests - successful_requests) / total_requests * 100,
            "duration_seconds": total_time,
            "requests_per_second": successful_requests / total_time,
            "latency_ms": {
                "min": min(all_latencies),
                "max": max(all_latencies),
                "mean": statistics.mean(all_latencies),
                "median": statistics.median(all_latencies),
                "p95": statistics.quantiles(all_latencies, n=20)[18] if len(all_latencies) > 20 else max(all_latencies),
                "p99": statistics.quantiles(all_latencies, n=100)[98] if len(all_latencies) > 100 else max(all_latencies),
            },
            "errors": total_errors[:20]  # 只保留前20个错误
        }
        
        print(f"   总用时: {total_time:.2f}秒")
        print(f"   吞吐量: {result['requests_per_second']:.1f} RPS") 
        print(f"   平均延迟: {result['latency_ms']['mean']:.2f}ms")
        print(f"   P95延迟: {result['latency_ms']['p95']:.2f}ms")
        print(f"   成功率: {successful_requests}/{total_requests} ({successful_requests/total_requests*100:.1f}%)")
        
        return result
    
    def test_message_size_impact(self, message_sizes: List[int] = None) -> Dict[str, Any]:
        """测试消息大小对性能的影响"""
        if message_sizes is None:
            message_sizes = [100, 1000, 10000, 100000]  # bytes
            
        print(f"📏 测试消息大小对性能的影响")
        
        results = {}
        
        for size in message_sizes:
            print(f"   测试消息大小: {size} bytes")
            
            # 生成指定大小的测试数据
            test_data = "x" * (size - 50)  # 减去基础消息开销
            
            latencies = []
            sock = self._connect_socket()
            
            # 进行认证握手
            if not self._authenticate_connection(sock):
                print(f"     认证失败")
                sock.close()
                continue
            
            try:
                for _ in range(20):  # 每个大小测试20次
                    try:
                        response, latency = self._send_ipc_message(
                            sock, 
                            "/health",
                            {"test_data": test_data}
                        )
                        latencies.append(latency)
                    except Exception as e:
                        print(f"     错误: {e}")
                        
            finally:
                sock.close()
            
            if latencies:
                results[f"{size}_bytes"] = {
                    "message_size": size,
                    "avg_latency_ms": statistics.mean(latencies),
                    "min_latency_ms": min(latencies),
                    "max_latency_ms": max(latencies)
                }
                print(f"     平均延迟: {statistics.mean(latencies):.2f}ms")
            else:
                results[f"{size}_bytes"] = {"error": "No successful requests"}
        
        return {"test": "message_size_impact", "results": results}
    
    def test_connection_establishment(self, num_connections: int = 50) -> Dict[str, Any]:
        """测试连接建立性能"""
        print(f"🔗 测试连接建立性能 (n={num_connections})")
        
        connection_times = []
        errors = []
        
        for i in range(num_connections):
            try:
                start_time = time.perf_counter()
                sock = self._connect_socket()
                end_time = time.perf_counter()
                
                connection_time = (end_time - start_time) * 1000
                connection_times.append(connection_time)
                
                sock.close()
                
            except Exception as e:
                errors.append(str(e))
        
        if not connection_times:
            return {"error": "No successful connections", "errors": errors}
        
        result = {
            "test": "connection_establishment",
            "total_attempts": num_connections,
            "successful_connections": len(connection_times),
            "error_rate": len(errors) / num_connections * 100,
            "connection_time_ms": {
                "min": min(connection_times),
                "max": max(connection_times),
                "mean": statistics.mean(connection_times),
                "median": statistics.median(connection_times)
            },
            "errors": errors[:10]
        }
        
        print(f"   平均连接时间: {result['connection_time_ms']['mean']:.2f}ms")
        print(f"   成功率: {len(connection_times)}/{num_connections} ({len(connection_times)/num_connections*100:.1f}%)")
        
        return result
    
    def run_full_benchmark(self) -> Dict[str, Any]:
        """运行完整性能基准测试"""
        print("🚀 开始IPC性能基准测试\n")
        
        results = {
            "timestamp": time.time(),
            "socket_path": self.socket_path,
            "tests": {}
        }
        
        # 1. 单次请求延迟测试
        results["tests"]["single_request_latency"] = self.test_single_request_latency(100)
        print()
        
        # 2. 并发请求测试  
        results["tests"]["concurrent_requests"] = self.test_concurrent_requests(10, 30)
        print()
        
        # 3. 消息大小影响测试
        results["tests"]["message_size_impact"] = self.test_message_size_impact()
        print()
        
        # 4. 连接建立性能测试
        results["tests"]["connection_establishment"] = self.test_connection_establishment(30)
        print()
        
        # 性能评估
        self._evaluate_performance(results)
        
        return results
    
    def _evaluate_performance(self, results: Dict[str, Any]):
        """评估性能结果"""
        print("📊 性能评估结果:")
        
        single_test = results["tests"].get("single_request_latency", {})
        concurrent_test = results["tests"].get("concurrent_requests", {})
        
        # 延迟评估
        if "latency_ms" in single_test:
            avg_latency = single_test["latency_ms"]["mean"]
            p95_latency = single_test["latency_ms"]["p95"]
            
            print(f"   🎯 延迟性能:")
            if avg_latency < 5:
                print(f"   ✅ 平均延迟: {avg_latency:.2f}ms (优秀 - <5ms)")
            elif avg_latency < 10:
                print(f"   ⚠️  平均延迟: {avg_latency:.2f}ms (良好 - <10ms)")
            else:
                print(f"   ❌ 平均延迟: {avg_latency:.2f}ms (需要优化 - >10ms)")
                
            if p95_latency < 10:
                print(f"   ✅ P95延迟: {p95_latency:.2f}ms (优秀 - <10ms)")
            elif p95_latency < 20:
                print(f"   ⚠️  P95延迟: {p95_latency:.2f}ms (可接受 - <20ms)")
            else:
                print(f"   ❌ P95延迟: {p95_latency:.2f}ms (需要优化 - >20ms)")
        
        # 吞吐量评估
        if "requests_per_second" in concurrent_test:
            rps = concurrent_test["requests_per_second"]
            
            print(f"   🚀 吞吐量性能:")
            if rps > 1000:
                print(f"   ✅ 吞吐量: {rps:.1f} RPS (优秀 - >1000)")
            elif rps > 500:
                print(f"   ⚠️  吞吐量: {rps:.1f} RPS (良好 - >500)")
            else:
                print(f"   ❌ 吞吐量: {rps:.1f} RPS (需要优化 - <500)")
        
        # 稳定性评估
        single_error_rate = single_test.get("error_rate", 100)
        concurrent_error_rate = concurrent_test.get("error_rate", 100)
        
        print(f"   🛡️  稳定性评估:")
        if single_error_rate < 1 and concurrent_error_rate < 1:
            print(f"   ✅ 错误率: 单次{single_error_rate:.1f}% 并发{concurrent_error_rate:.1f}% (优秀)")
        elif single_error_rate < 5 and concurrent_error_rate < 5:
            print(f"   ⚠️  错误率: 单次{single_error_rate:.1f}% 并发{concurrent_error_rate:.1f}% (可接受)")
        else:
            print(f"   ❌ 错误率: 单次{single_error_rate:.1f}% 并发{concurrent_error_rate:.1f}% (需要优化)")


def main():
    """主函数"""
    # 读取socket配置
    socket_config_file = Path.home() / '.linch-mind' / 'daemon.socket'
    
    if not socket_config_file.exists():
        print("❌ 找不到daemon socket配置文件")
        print("   请确保daemon正在运行: ./linch-mind daemon start")
        return
    
    with open(socket_config_file) as f:
        socket_config = json.load(f)
    
    socket_path = socket_config.get("path")
    if not socket_path:
        print("❌ Socket配置中找不到path")
        return
        
    print(f"🎯 使用Socket: {socket_path}")
    print(f"📋 Daemon PID: {socket_config.get('pid')}")
    print()
    
    # 验证socket可用性
    try:
        test_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        test_sock.connect(socket_path)
        test_sock.close()
        print("✅ IPC连接测试成功")
        print()
    except Exception as e:
        print(f"❌ IPC连接测试失败: {e}")
        return
    
    # 运行基准测试
    benchmark = IPCPerformanceBenchmark(socket_path)
    results = benchmark.run_full_benchmark()
    
    # 保存结果
    results_file = Path("ipc_benchmark_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"📁 详细结果已保存到: {results_file}")


if __name__ == "__main__":
    main()