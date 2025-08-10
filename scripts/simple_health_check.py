#!/usr/bin/env python3
"""
简单健康检查 - 通过进程和文件检查系统状态
"""

import subprocess
import os
from pathlib import Path

def check_processes():
    """检查关键进程"""
    print("🔍 检查系统进程...")
    
    try:
        # 检查daemon进程
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        processes = result.stdout
        
        daemon_running = False
        clipboard_running = False
        filesystem_running = False
        
        for line in processes.split('\n'):
            if 'linch-mind' in line.lower() and 'daemon' in line:
                daemon_running = True
                print("✅ Daemon进程运行中")
            elif 'linch-mind-clipboard' in line:
                clipboard_running = True  
                print("✅ 剪贴板连接器运行中")
            elif 'linch-mind-filesystem' in line:
                filesystem_running = True
                print("✅ 文件系统连接器运行中")
        
        if not daemon_running:
            print("❌ Daemon进程未找到")
        
        return daemon_running
        
    except Exception as e:
        print(f"❌ 进程检查失败: {e}")
        return False

def check_socket_files():
    """检查IPC socket文件"""
    print("\n🔍 检查IPC通信文件...")
    
    # 检查用户目录下的socket文件
    home = Path.home()
    linch_dir = home / ".linch-mind"
    
    if linch_dir.exists():
        print(f"✅ Linch Mind数据目录存在: {linch_dir}")
        
        # 查找socket文件
        daemon_socket = linch_dir / "daemon.socket"
        if daemon_socket.exists():
            print(f"✅ Daemon socket文件存在: {daemon_socket}")
            return True
        else:
            # 查找临时socket文件
            import glob
            temp_sockets = glob.glob("/var/folders/*/T/linch-mind-*.sock") + \
                          glob.glob("/tmp/linch-mind-*.sock")
            if temp_sockets:
                print(f"✅ 临时socket文件存在: {temp_sockets[0]}")
                return True
            else:
                print("❌ 未找到socket文件")
                return False
    else:
        print(f"❌ Linch Mind数据目录不存在: {linch_dir}")
        return False

def main():
    print("🚀 Linch Mind 简单健康检查\n")
    
    process_ok = check_processes()
    socket_ok = check_socket_files()
    
    print(f"\n📊 系统状态总结:")
    print(f"  进程状态: {'✅ 正常' if process_ok else '❌ 异常'}")
    print(f"  IPC通信: {'✅ 正常' if socket_ok else '❌ 异常'}")
    
    if process_ok and socket_ok:
        print("\n🎉 系统运行正常！")
        return True
    else:
        print("\n⚠️ 系统存在问题，建议重启")
        return False

if __name__ == "__main__":
    main()