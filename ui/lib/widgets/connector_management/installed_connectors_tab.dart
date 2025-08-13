import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/connector_lifecycle_models.dart';
import '../../services/connector_lifecycle_api_client.dart';
import '../../core/ui_service_facade.dart';
import 'installed_connector_card.dart';
import 'installed_search_filter.dart';
import 'installed_status_overview.dart';

/// 已安装连接器Tab页面
class InstalledConnectorsTab extends ConsumerStatefulWidget {
  const InstalledConnectorsTab({super.key});

  @override
  ConsumerState<InstalledConnectorsTab> createState() =>
      _InstalledConnectorsTabState();
}

class _InstalledConnectorsTabState
    extends ConsumerState<InstalledConnectorsTab> {
  final _apiClient = getService<ConnectorLifecycleApiClient>();

  List<ConnectorInfo> _installedConnectors = [];
  bool _installedLoading = true;
  String? _installedErrorMessage;
  String _installedSearchQuery = '';

  @override
  void initState() {
    super.initState();
    _loadInstalledConnectors();
  }

  Future<void> _loadInstalledConnectors() async {
    setState(() {
      _installedLoading = true;
      _installedErrorMessage = null;
    });

    try {
      final connectorResponse = await _apiClient.getConnectors();
      setState(() {
        _installedConnectors = connectorResponse.connectors;
        _installedLoading = false;
      });
    } catch (e) {
      setState(() {
        _installedErrorMessage = '加载连接器失败: $e';
        _installedLoading = false;
      });
    }
  }

  Future<void> _refreshInstalledConnectors() async {
    await _loadInstalledConnectors();
  }

  List<ConnectorInfo> get _filteredInstalledConnectors {
    if (_installedSearchQuery.isEmpty) return _installedConnectors;
    return _installedConnectors
        .where((connector) =>
            connector.displayName
                .toLowerCase()
                .contains(_installedSearchQuery.toLowerCase()) ||
            connector.connectorId
                .toLowerCase()
                .contains(_installedSearchQuery.toLowerCase()))
        .toList();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        InstalledSearchAndFilter(
          searchQuery: _installedSearchQuery,
          onSearchChanged: (query) {
            setState(() {
              _installedSearchQuery = query;
            });
          },
          onRefresh: _refreshInstalledConnectors,
        ),
        InstalledStatusOverview(connectors: _installedConnectors),
        Expanded(
          child: _buildContent(),
        ),
      ],
    );
  }

  Widget _buildContent() {
    if (_installedLoading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('加载已安装连接器...'),
          ],
        ),
      );
    }

    if (_installedErrorMessage != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red[300],
            ),
            const SizedBox(height: 16),
            Text(
              _installedErrorMessage!,
              style: TextStyle(color: Colors.red[300]),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              icon: const Icon(Icons.refresh),
              label: const Text('重试'),
              onPressed: _refreshInstalledConnectors,
            ),
          ],
        ),
      );
    }

    final filteredConnectors = _filteredInstalledConnectors;

    if (filteredConnectors.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              _installedSearchQuery.isNotEmpty
                  ? Icons.search_off
                  : Icons.extension,
              size: 64,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            Text(
              _installedSearchQuery.isNotEmpty ? '没有找到匹配的连接器' : '还没有安装连接器',
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
        final crossAxisCount = (constraints.maxWidth / 350).floor().clamp(1, 4);
        return GridView.builder(
          padding: const EdgeInsets.all(16),
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: crossAxisCount,
            childAspectRatio: 5.0,
            crossAxisSpacing: 16,
            mainAxisSpacing: 16,
          ),
          itemCount: filteredConnectors.length,
          itemBuilder: (context, index) {
            return InstalledConnectorCard(
              connector: filteredConnectors[index],
              onRefresh: _refreshInstalledConnectors,
            );
          },
        );
      },
    );
  }
}
