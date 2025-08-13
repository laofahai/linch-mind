// 向量搜索界面 - 核心功能版本
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../widgets/vector_search/smart_search_widget.dart';
import '../widgets/vector_search/search_results_widget.dart';
import '../widgets/vector_search/network_graph_widget.dart';

class VectorSearchScreen extends ConsumerStatefulWidget {
  const VectorSearchScreen({super.key});

  @override
  ConsumerState<VectorSearchScreen> createState() => _VectorSearchScreenState();
}

class _VectorSearchScreenState extends ConsumerState<VectorSearchScreen> {
  String? _selectedEntityId;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('智能语义搜索'),
        backgroundColor: theme.colorScheme.surface,
      ),
      body: Column(
        children: [
          // 搜索框
          SmartSearchWidget(
            onSearchSubmitted: (query) {
              // 搜索提交后的回调（可选）
            },
          ),
          
          // 主要内容
          Expanded(
            child: Row(
              children: [
                // 搜索结果区域
                Expanded(
                  flex: 2,
                  child: SearchResultsWidget(
                    onResultTap: (result) {
                      setState(() {
                        _selectedEntityId = result.entityId;
                      });
                    },
                    onSimilarityTap: (entityId) {
                      setState(() {
                        _selectedEntityId = entityId;
                      });
                    },
                  ),
                ),
                
                // 分隔线
                const VerticalDivider(width: 1),
                
                // 知识图谱区域
                Expanded(
                  flex: 1,
                  child: NetworkGraphWidget(
                    entityId: _selectedEntityId,
                    onNodeTap: (entityId) {
                      setState(() {
                        _selectedEntityId = entityId;
                      });
                    },
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}