import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/connector_lifecycle_models.dart';
import '../../services/registry_api_client.dart';
import '../../config/app_constants.dart';

/// 市场连接器Tab页面
class MarketConnectorsTab extends ConsumerStatefulWidget {
  const MarketConnectorsTab({super.key});

  @override
  ConsumerState<MarketConnectorsTab> createState() =>
      _MarketConnectorsTabState();
}

class _MarketConnectorsTabState extends ConsumerState<MarketConnectorsTab> {
  List<ConnectorDefinition> _marketConnectors = [];
  bool _marketLoading = false;
  String? _marketErrorMessage;
  String _marketSearchQuery = '';

  @override
  void initState() {
    super.initState();
    _loadMarketConnectors();
  }

  Future<void> _loadMarketConnectors() async {
    if (_marketConnectors.isNotEmpty) return; // 已加载过

    setState(() {
      _marketLoading = true;
      _marketErrorMessage = null;
    });

    try {
      final marketConnectors = await RegistryApiClient.getMarketConnectors();
      setState(() {
        _marketConnectors = marketConnectors;
        _marketLoading = false;
      });
    } catch (e) {
      setState(() {
        _marketErrorMessage = '加载市场连接器失败: $e';
        _marketLoading = false;
      });
    }
  }

  Future<void> _refreshMarketConnectors() async {
    _marketConnectors.clear();
    await _loadMarketConnectors();
  }

  List<ConnectorDefinition> get _filteredMarketConnectors {
    if (_marketSearchQuery.isEmpty) return _marketConnectors;
    return _marketConnectors
        .where((connector) =>
            connector.name.toLowerCase().contains(_marketSearchQuery.toLowerCase()) ||
            connector.description.toLowerCase().contains(_marketSearchQuery.toLowerCase()))
        .toList();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _buildSearchAndCategory(),
        Expanded(
          child: _buildContent(),
        ),
      ],
    );
  }

  Widget _buildSearchAndCategory() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              decoration: InputDecoration(
                hintText: '搜索市场连接器...',
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
              ),
              onChanged: (query) {
                setState(() {
                  _marketSearchQuery = query;
                });
              },
            ),
          ),
          const SizedBox(width: 16),
          IconButton.filled(
            icon: const Icon(Icons.refresh),
            onPressed: _refreshMarketConnectors,
            tooltip: '刷新',
          ),
        ],
      ),
    );
  }

  Widget _buildContent() {
    if (_marketLoading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('加载市场连接器...'),
          ],
        ),
      );
    }

    if (_marketErrorMessage != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.cloud_off,
              size: 64,
              color: Colors.red[300],
            ),
            const SizedBox(height: 16),
            Text(
              _marketErrorMessage!,
              style: TextStyle(color: Colors.red[300]),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              icon: const Icon(Icons.refresh),
              label: const Text('重试'),
              onPressed: _refreshMarketConnectors,
            ),
          ],
        ),
      );
    }

    final filteredConnectors = _filteredMarketConnectors;

    if (filteredConnectors.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              _marketSearchQuery.isNotEmpty 
                  ? Icons.search_off 
                  : Icons.store,
              size: 64,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            Text(
              _marketSearchQuery.isNotEmpty
                  ? '没有找到匹配的连接器'
                  : '市场连接器暂时不可用',
              style: TextStyle(
                fontSize: 18,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      );
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        final crossAxisCount = context.calculateGridColumns();
        return GridView.builder(
          padding: const EdgeInsets.all(AppLayoutConstants.padding),
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: crossAxisCount,
            childAspectRatio: AppLayoutConstants.marketGridChildAspectRatio,
            crossAxisSpacing: AppLayoutConstants.gridCrossAxisSpacing,
            mainAxisSpacing: AppLayoutConstants.gridMainAxisSpacing,
          ),
          itemCount: filteredConnectors.length,
          itemBuilder: (context, index) {
            final connector = filteredConnectors[index];
            return Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      connector.name,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      connector.description,
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 14,
                      ),
                      maxLines: 3,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const Spacer(),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'v${connector.version}',
                          style: TextStyle(
                            color: Colors.grey[500],
                            fontSize: 12,
                          ),
                        ),
                        ElevatedButton(
                          onPressed: () {
                            // TODO: 实现安装功能
                          },
                          child: const Text('安装'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }
}