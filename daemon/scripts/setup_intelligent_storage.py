#!/usr/bin/env python3
"""
智能存储环境设置脚本
自动设置Ollama模型、存储目录结构和初始化配置
"""

import asyncio
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiohttp

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.intelligent_storage import get_config_manager, get_intelligent_storage_config
from core.environment_manager import get_environment_manager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IntelligentStorageSetup:
    """智能存储环境设置器"""
    
    def __init__(self):
        self.config_manager = get_config_manager()
        self.config = get_intelligent_storage_config()
        self.env_manager = get_environment_manager()
        
        # Ollama连接设置
        self.ollama_host = self.config.ollama.host
        self.embedding_model = self.config.ollama.embedding_model
        self.llm_model = self.config.ollama.llm_model
        
        # 所需模型列表
        self.required_models = [
            self.embedding_model,
            self.llm_model,
        ]

    async def setup_complete_environment(self) -> bool:
        """设置完整的智能存储环境"""
        try:
            logger.info("🚀 开始设置智能存储环境...")
            
            # 1. 检查系统依赖
            if not await self._check_system_dependencies():
                return False
            
            # 2. 设置存储目录结构
            await self._setup_storage_directories()
            
            # 3. 检查和安装Ollama
            if not await self._setup_ollama():
                return False
            
            # 4. 下载必需模型
            if not await self._download_required_models():
                return False
            
            # 5. 验证模型可用性
            if not await self._verify_models():
                return False
            
            # 6. 生成配置文件
            await self._generate_config_files()
            
            # 7. 初始化存储结构
            await self._initialize_storage_structure()
            
            # 8. 运行系统测试
            if not await self._run_system_tests():
                logger.warning("系统测试失败，但环境设置已完成")
            
            logger.info("✅ 智能存储环境设置完成！")
            return True
            
        except Exception as e:
            logger.error(f"环境设置失败: {e}")
            return False

    # === 系统依赖检查 ===

    async def _check_system_dependencies(self) -> bool:
        """检查系统依赖"""
        logger.info("🔍 检查系统依赖...")
        
        # 检查Python包
        required_packages = [
            "faiss-cpu",
            "aiohttp", 
            "numpy",
            "sqlalchemy",
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"缺少必需的Python包: {missing_packages}")
            logger.info("请运行: pip install " + " ".join(missing_packages))
            return False
        
        # 检查可选包
        optional_packages = ["psutil", "sentence-transformers"]
        for package in optional_packages:
            try:
                __import__(package.replace("-", "_"))
                logger.info(f"✅ 可选包已安装: {package}")
            except ImportError:
                logger.warning(f"⚠️  建议安装可选包: {package}")
        
        logger.info("✅ 系统依赖检查完成")
        return True

    # === 存储目录设置 ===

    async def _setup_storage_directories(self):
        """设置存储目录结构"""
        logger.info("📁 设置存储目录结构...")
        
        directories = [
            self.config.storage_dir,
            self.config.storage_dir / "hot_index",
            self.config.storage_dir / "warm_index", 
            self.config.storage_dir / "cold_archive",
            self.config.cache_dir,
            self.config.temp_dir,
            self.config.storage_dir / "backups",
            self.config.storage_dir / "logs",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"创建目录: {directory}")
        
        # 创建README文件
        readme_content = """# Linch Mind 智能存储目录结构

## 目录说明

- `hot_index/`: 热数据索引 (最近90天的高频访问数据)
- `warm_index/`: 温数据索引 (90天-1年的中频访问数据)  
- `cold_archive/`: 冷数据归档 (1年以上的低频访问数据)
- `ollama_cache/`: Ollama模型缓存和响应缓存
- `temp/`: 临时文件目录
- `backups/`: 数据备份目录
- `logs/`: 存储系统日志

## 数据生命周期

1. 新数据进入 `hot_index/` 进行实时处理和频繁访问
2. 90天后自动迁移到 `warm_index/` 进行中等频率访问
3. 1年后压缩并归档到 `cold_archive/` 进行长期保存
4. 3年后根据价值评分决定是否永久删除

## 注意事项

- 不要手动修改索引文件，请使用提供的API接口
- 定期备份 `hot_index/` 和 `warm_index/` 中的重要数据
- `temp/` 目录会自动清理，不要存放重要文件
"""
        
        readme_file = self.config.storage_dir / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        logger.info(f"✅ 存储目录结构设置完成: {self.config.storage_dir}")

    # === Ollama设置 ===

    async def _setup_ollama(self) -> bool:
        """设置Ollama"""
        logger.info("🤖 设置Ollama...")
        
        # 检查Ollama是否已安装
        if not await self._check_ollama_installed():
            logger.info("Ollama未安装，开始安装...")
            if not await self._install_ollama():
                return False
        
        # 启动Ollama服务
        if not await self._start_ollama_service():
            return False
        
        # 验证连接
        if not await self._check_ollama_connection():
            return False
        
        logger.info("✅ Ollama设置完成")
        return True

    async def _check_ollama_installed(self) -> bool:
        """检查Ollama是否已安装"""
        try:
            result = subprocess.run(["ollama", "--version"], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Ollama已安装: {result.stdout.strip()}")
                return True
            return False
        except FileNotFoundError:
            return False

    async def _install_ollama(self) -> bool:
        """安装Ollama"""
        try:
            logger.info("正在下载和安装Ollama...")
            
            # macOS/Linux安装脚本
            install_cmd = "curl -fsSL https://ollama.com/install.sh | sh"
            process = await asyncio.create_subprocess_shell(
                install_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info("✅ Ollama安装成功")
                return True
            else:
                logger.error(f"Ollama安装失败: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"安装Ollama时出错: {e}")
            return False

    async def _start_ollama_service(self) -> bool:
        """启动Ollama服务"""
        try:
            # 检查服务是否已运行
            if await self._check_ollama_connection():
                logger.info("✅ Ollama服务已在运行")
                return True
            
            logger.info("启动Ollama服务...")
            
            # 后台启动Ollama
            process = await asyncio.create_subprocess_exec(
                "ollama", "serve",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            
            # 等待服务启动
            await asyncio.sleep(3)
            
            # 验证服务启动
            if await self._check_ollama_connection():
                logger.info("✅ Ollama服务启动成功")
                return True
            else:
                logger.error("Ollama服务启动失败")
                return False
                
        except Exception as e:
            logger.error(f"启动Ollama服务时出错: {e}")
            return False

    async def _check_ollama_connection(self) -> bool:
        """检查Ollama连接"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_host}/api/tags") as response:
                    if response.status == 200:
                        return True
            return False
        except Exception:
            return False

    # === 模型下载 ===

    async def _download_required_models(self) -> bool:
        """下载必需模型"""
        logger.info("📥 下载必需的AI模型...")
        
        for model in self.required_models:
            if not await self._download_model(model):
                logger.error(f"模型下载失败: {model}")
                return False
        
        logger.info("✅ 所有必需模型下载完成")
        return True

    async def _download_model(self, model: str) -> bool:
        """下载单个模型"""
        try:
            # 检查模型是否已存在
            if await self._check_model_exists(model):
                logger.info(f"✅ 模型已存在: {model}")
                return True
            
            logger.info(f"📥 下载模型: {model}")
            
            # 使用ollama pull命令下载
            process = await asyncio.create_subprocess_exec(
                "ollama", "pull", model,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # 显示下载进度
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                logger.info(f"下载进度: {line.decode().strip()}")
            
            await process.wait()
            
            if process.returncode == 0:
                logger.info(f"✅ 模型下载成功: {model}")
                return True
            else:
                stderr = await process.stderr.read()
                logger.error(f"模型下载失败: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"下载模型时出错 [{model}]: {e}")
            return False

    async def _check_model_exists(self, model: str) -> bool:
        """检查模型是否存在"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_host}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        models = {m["name"] for m in data.get("models", [])}
                        return model in models
            return False
        except Exception:
            return False

    # === 模型验证 ===

    async def _verify_models(self) -> bool:
        """验证模型功能"""
        logger.info("🧪 验证模型功能...")
        
        # 测试嵌入模型
        if not await self._test_embedding_model():
            return False
        
        # 测试LLM模型
        if not await self._test_llm_model():
            return False
        
        logger.info("✅ 模型功能验证完成")
        return True

    async def _test_embedding_model(self) -> bool:
        """测试嵌入模型"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_host}/api/embeddings",
                    json={
                        "model": self.embedding_model,
                        "prompt": "测试文本向量化功能"
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        embedding = data.get("embedding", [])
                        if len(embedding) == 384:  # nomic-embed-text维度
                            logger.info(f"✅ 嵌入模型测试成功: {self.embedding_model}")
                            return True
            
            logger.error(f"嵌入模型测试失败: {self.embedding_model}")
            return False
            
        except Exception as e:
            logger.error(f"测试嵌入模型时出错: {e}")
            return False

    async def _test_llm_model(self) -> bool:
        """测试LLM模型"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": self.llm_model,
                        "prompt": "请回复'模型测试成功'",
                        "stream": False
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response", "")
                        if "成功" in response_text or "success" in response_text.lower():
                            logger.info(f"✅ LLM模型测试成功: {self.llm_model}")
                            return True
            
            logger.error(f"LLM模型测试失败: {self.llm_model}")
            return False
            
        except Exception as e:
            logger.error(f"测试LLM模型时出错: {e}")
            return False

    # === 配置文件生成 ===

    async def _generate_config_files(self):
        """生成配置文件"""
        logger.info("📝 生成配置文件...")
        
        # 生成配置模板
        config_template_path = self.config.storage_dir / "config_template.json"
        self.config_manager.save_config_template(config_template_path)
        
        # 导出当前配置
        current_config_path = self.config.storage_dir / "current_config.json"
        self.config_manager.export_current_config(current_config_path)
        
        # 生成环境变量文件
        env_file_path = self.config.storage_dir / ".env.example"
        env_content = f"""# Linch Mind 智能存储环境变量

# Ollama配置
OLLAMA_HOST={self.ollama_host}
OLLAMA_EMBEDDING_MODEL={self.embedding_model}
OLLAMA_LLM_MODEL={self.llm_model}

# 处理配置
ENABLE_INTELLIGENT_PROCESSING=true
AI_VALUE_THRESHOLD={self.config.ollama.value_threshold}

# 存储配置
STORAGE_DIR={self.config.storage_dir}
CACHE_DIR={self.config.cache_dir}

# 调试配置
DEBUG={str(self.config.debug).lower()}
ENVIRONMENT={self.config.environment}
"""
        
        with open(env_file_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        logger.info(f"✅ 配置文件生成完成: {self.config.storage_dir}")

    # === 存储结构初始化 ===

    async def _initialize_storage_structure(self):
        """初始化存储结构"""
        logger.info("🗃️  初始化存储结构...")
        
        # 创建分片元数据文件
        shard_metadata = {
            "shards": [],
            "version": "1.0",
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
        }
        
        metadata_file = self.config.storage_dir / "shard_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(shard_metadata, f, ensure_ascii=False, indent=2)
        
        # 创建统计文件
        stats_file = self.config.storage_dir / "storage_stats.json"
        initial_stats = {
            "total_documents": 0,
            "total_shards": 0,
            "storage_size_mb": 0.0,
            "last_updated": datetime.utcnow().isoformat(),
        }
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(initial_stats, f, ensure_ascii=False, indent=2)
        
        logger.info("✅ 存储结构初始化完成")

    # === 系统测试 ===

    async def _run_system_tests(self) -> bool:
        """运行系统测试"""
        logger.info("🧪 运行系统测试...")
        
        try:
            # 导入并测试核心组件
            from services.ai.ollama_service import OllamaService
            from services.storage.faiss_vector_store import FAISSVectorStore
            from services.storage.intelligent_event_processor import IntelligentEventProcessor
            
            # 测试Ollama服务
            ollama_service = OllamaService(
                ollama_host=self.ollama_host,
                embedding_model=self.embedding_model,
                llm_model=self.llm_model,
            )
            
            if not await ollama_service.initialize():
                logger.error("Ollama服务初始化测试失败")
                return False
            
            # 测试内容评估
            test_score = await ollama_service.evaluate_content_value("这是一个测试内容")
            if 0.0 <= test_score <= 1.0:
                logger.info(f"✅ 内容评估测试成功: {test_score:.3f}")
            else:
                logger.error("内容评估测试失败")
                return False
            
            # 测试向量存储
            vector_store = FAISSVectorStore(storage_dir=self.config.storage_dir)
            if not await vector_store.initialize():
                logger.error("向量存储初始化测试失败")
                return False
            
            await ollama_service.close()
            await vector_store.close()
            
            logger.info("✅ 系统测试完成")
            return True
            
        except Exception as e:
            logger.error(f"系统测试失败: {e}")
            return False

    # === 公共接口 ===

    async def check_environment_status(self) -> Dict[str, bool]:
        """检查环境状态"""
        status = {
            "ollama_installed": await self._check_ollama_installed(),
            "ollama_running": await self._check_ollama_connection(),
            "models_available": True,
            "storage_dirs": True,
        }
        
        # 检查模型
        for model in self.required_models:
            if not await self._check_model_exists(model):
                status["models_available"] = False
                break
        
        # 检查存储目录
        required_dirs = [
            self.config.storage_dir,
            self.config.cache_dir,
            self.config.temp_dir,
        ]
        
        for directory in required_dirs:
            if not directory.exists():
                status["storage_dirs"] = False
                break
        
        return status

    async def repair_environment(self) -> bool:
        """修复环境问题"""
        logger.info("🔧 修复环境问题...")
        
        status = await self.check_environment_status()
        
        # 修复Ollama
        if not status["ollama_installed"]:
            if not await self._install_ollama():
                return False
        
        if not status["ollama_running"]:
            if not await self._start_ollama_service():
                return False
        
        # 修复模型
        if not status["models_available"]:
            if not await self._download_required_models():
                return False
        
        # 修复存储目录
        if not status["storage_dirs"]:
            await self._setup_storage_directories()
        
        logger.info("✅ 环境修复完成")
        return True


async def main():
    """主函数"""
    setup = IntelligentStorageSetup()
    
    print("🚀 Linch Mind 智能存储环境设置")
    print("=" * 50)
    
    # 检查当前状态
    status = await setup.check_environment_status()
    print(f"当前环境状态:")
    for key, value in status.items():
        status_icon = "✅" if value else "❌"
        print(f"  {status_icon} {key}: {value}")
    
    print()
    
    # 如果环境不完整，进行设置
    if not all(status.values()):
        confirm = input("是否继续设置智能存储环境? (y/N): ")
        if confirm.lower() in ('y', 'yes'):
            success = await setup.setup_complete_environment()
            if success:
                print("\n🎉 智能存储环境设置成功！")
                print(f"存储目录: {setup.config.storage_dir}")
                print(f"缓存目录: {setup.config.cache_dir}")
                print(f"Ollama主机: {setup.ollama_host}")
            else:
                print("\n❌ 环境设置失败，请检查错误信息")
                return 1
        else:
            print("取消设置")
            return 0
    else:
        print("✅ 环境已正确设置，无需额外操作")
    
    return 0


if __name__ == "__main__":
    import sys
    from datetime import datetime
    
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断设置")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 设置过程中出现错误: {e}")
        sys.exit(1)