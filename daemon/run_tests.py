#!/usr/bin/env python3
"""
测试运行器 - 用于运行daemon测试套件
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """运行测试套件"""
    print("🚀 开始运行Linch Mind Daemon测试套件...")
    
    # 确保在正确的目录
    os.chdir(Path(__file__).parent)
    
    # 运行pytest配置检查
    print("\n📋 检查pytest配置...")
    result = subprocess.run([
        "poetry", "run", "python", "-m", "pytest", 
        "--collect-only", "-q"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ pytest配置检查失败: {result.stderr}")
        return False
    
    collected_tests = result.stdout.count("::test_")
    print(f"✅ 发现 {collected_tests} 个测试用例")
    
    # 运行测试
    print("\n🧪 运行测试...")
    test_cmd = [
        "poetry", "run", "python", "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--strict-markers",
        "-x",  # 第一个失败时停止
        "--disable-warnings"  # 暂时禁用警告以保持输出清洁
    ]
    
    result = subprocess.run(test_cmd)
    
    if result.returncode == 0:
        print("\n✅ 所有测试通过!")
        
        # 运行代码覆盖率检查
        print("\n📊 运行代码覆盖率分析...")
        coverage_cmd = [
            "poetry", "run", "python", "-m", "pytest",
            "tests/",
            "--cov=.",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-fail-under=70",  # 要求至少70%覆盖率
            "--disable-warnings"
        ]
        
        coverage_result = subprocess.run(coverage_cmd)
        
        if coverage_result.returncode == 0:
            print("\n🎉 测试套件完成! 覆盖率达标!")
            print("📈 详细覆盖率报告已生成到 htmlcov/ 目录")
            return True
        else:
            print("\n⚠️  测试通过但覆盖率未达标（需要>70%）")
            return False
    else:
        print(f"\n❌ 测试失败，退出码: {result.returncode}")
        return False

def main():
    """主函数"""
    success = run_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()