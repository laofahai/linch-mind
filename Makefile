# Linch Mind 连接器管理 Makefile

PYTHON := python3
SCRIPTS_DIR := scripts
CONNECTORS_DIR := connectors
DIST_DIR := dist/connectors

.PHONY: help setup check package docs clean all

# 显示帮助信息
help:
	@echo "Linch Mind 连接器管理工具"
	@echo ""
	@echo "可用命令："
	@echo "  setup           - 创建必要的目录结构"
	@echo "  check           - 检查所有连接器结构"
	@echo "  check-<id>      - 检查指定连接器 (如: check-filesystem)"
	@echo "  package         - 打包所有连接器"
	@echo "  package-<id>    - 打包指定连接器 (如: package-filesystem)"
	@echo "  docs            - 生成所有连接器文档"
	@echo "  docs-<id>       - 生成指定连接器文档 (如: docs-filesystem)"
	@echo "  clean           - 清理构建文件"
	@echo "  all             - 执行完整的检查+打包+文档生成流程"
	@echo ""
	@echo "示例："
	@echo "  make check-filesystem    # 检查文件系统连接器"
	@echo "  make package-clipboard   # 打包剪贴板连接器"
	@echo "  make all                # 完整流程"

# 创建目录结构
setup:
	@echo "📁 创建目录结构..."
	@mkdir -p $(DIST_DIR)
	@mkdir -p $(CONNECTORS_DIR)/examples
	@echo "✅ 目录结构创建完成"

# 检查所有连接器
check:
	@echo "🔍 检查所有连接器..."
	@$(PYTHON) $(SCRIPTS_DIR)/maintain-connectors.py --all

# 检查指定连接器
check-%:
	@echo "🔍 检查连接器: $*"
	@$(PYTHON) $(SCRIPTS_DIR)/maintain-connectors.py $* --full

# 打包所有连接器
package: setup
	@echo "📦 打包所有连接器..."
	@$(PYTHON) $(SCRIPTS_DIR)/package-connector.py --all --output $(DIST_DIR)

# 打包指定连接器
package-%: setup
	@echo "📦 打包连接器: $*"
	@$(PYTHON) $(SCRIPTS_DIR)/package-connector.py $* --output $(DIST_DIR)

# 生成所有连接器文档
docs:
	@echo "📖 生成所有连接器文档..."
	@for connector in filesystem clipboard; do \
		echo "生成 $$connector 文档..."; \
		$(PYTHON) $(SCRIPTS_DIR)/maintain-connectors.py $$connector --docs; \
	done

# 生成指定连接器文档
docs-%:
	@echo "📖 生成连接器文档: $*"
	@$(PYTHON) $(SCRIPTS_DIR)/maintain-connectors.py $* --docs

# 清理构建文件
clean:
	@echo "🧹 清理构建文件..."
	@rm -rf $(DIST_DIR)/*.zip
	@rm -rf __pycache__
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete
	@echo "✅ 清理完成"

# 列出可用连接器
list:
	@echo "🔌 可用连接器:"
	@$(PYTHON) $(SCRIPTS_DIR)/package-connector.py --list

# 完整流程
all: setup check package docs
	@echo ""
	@echo "🎉 完整流程执行完成！"
	@echo ""
	@echo "📊 构建结果:"
	@ls -la $(DIST_DIR)/ 2>/dev/null || echo "  无构建文件"

# 验证构建结果
verify:
	@echo "✅ 验证构建结果..."
	@if [ -d "$(DIST_DIR)" ]; then \
		echo "构建目录存在: $(DIST_DIR)"; \
		echo "包文件:"; \
		ls -la $(DIST_DIR)/*.zip 2>/dev/null || echo "  暂无包文件"; \
	else \
		echo "❌ 构建目录不存在"; \
	fi

# 开发环境设置
dev-setup:
	@echo "🔧 设置开发环境..."
	@pip install -r requirements.txt 2>/dev/null || echo "无requirements.txt文件"
	@echo "✅ 开发环境设置完成"

# 快速测试单个连接器
test-%:
	@echo "🧪 快速测试连接器: $*"
	@$(PYTHON) $(SCRIPTS_DIR)/maintain-connectors.py $* --check
	@$(PYTHON) $(SCRIPTS_DIR)/maintain-connectors.py $* --validate