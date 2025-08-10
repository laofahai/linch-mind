import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../widgets/connector_management/installed_connectors_tab.dart';
import '../widgets/connector_management/market_connectors_tab.dart';

/// 连接器管理主界面 - 重构版本
/// 拆分为多个独立组件，提高可维护性
class ConnectorManagementScreenRefactored extends ConsumerStatefulWidget {
  const ConnectorManagementScreenRefactored({super.key});

  @override
  ConsumerState<ConnectorManagementScreenRefactored> createState() =>
      _ConnectorManagementScreenRefactoredState();
}

class _ConnectorManagementScreenRefactoredState
    extends ConsumerState<ConnectorManagementScreenRefactored>
    with TickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('连接器管理'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(
              icon: Icon(Icons.extension),
              text: '已安装',
            ),
            Tab(
              icon: Icon(Icons.store),
              text: '市场',
            ),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: const [
          InstalledConnectorsTab(),
          MarketConnectorsTab(),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showAddConnectorDialog,
        tooltip: '添加连接器',
        child: const Icon(Icons.add),
      ),
    );
  }

  Future<void> _showAddConnectorDialog() async {
    // TODO: 实现添加连接器对话框
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('添加连接器'),
        content: const Text('此功能正在开发中...'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }
}
