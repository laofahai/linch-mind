import 'package:flutter/material.dart';

/// 已安装连接器的搜索和过滤组件
class InstalledSearchAndFilter extends StatelessWidget {
  final String searchQuery;
  final Function(String) onSearchChanged;
  final VoidCallback onRefresh;

  const InstalledSearchAndFilter({
    super.key,
    required this.searchQuery,
    required this.onSearchChanged,
    required this.onRefresh,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              decoration: InputDecoration(
                hintText: '搜索连接器...',
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
              ),
              onChanged: onSearchChanged,
            ),
          ),
          const SizedBox(width: 16),
          IconButton.filled(
            icon: const Icon(Icons.refresh),
            onPressed: onRefresh,
            tooltip: '刷新',
          ),
        ],
      ),
    );
  }
}
