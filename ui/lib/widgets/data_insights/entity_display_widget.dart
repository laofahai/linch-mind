// 智能实体展示组件
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/data_insights_models.dart';
import '../../providers/data_insights_provider.dart';
import '../../utils/app_logger.dart';
import 'responsive_dashboard_layout.dart';

/// 智能实体展示组件
class EntityDisplayWidget extends ConsumerStatefulWidget {
  final String? selectedType;
  final bool showAllTypes;

  const EntityDisplayWidget({
    super.key,
    this.selectedType,
    this.showAllTypes = true,
  });

  @override
  ConsumerState<EntityDisplayWidget> createState() => _EntityDisplayWidgetState();
}

class _EntityDisplayWidgetState extends ConsumerState<EntityDisplayWidget>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  
  final List<String> _entityTypes = [
    'all',
    'url',
    'file_path',
    'email',
    'phone',
    'keyword',
  ];

  final Map<String, String> _typeLabels = {
    'all': '全部',
    'url': 'URL',
    'file_path': '文件路径',
    'email': '邮箱',
    'phone': '电话',
    'keyword': '关键词',
  };

  final Map<String, IconData> _typeIcons = {
    'all': Icons.apps,
    'url': Icons.link,
    'file_path': Icons.folder,
    'email': Icons.email,
    'phone': Icons.phone,
    'keyword': Icons.tag,
  };

  @override
  void initState() {
    super.initState();
    _tabController = TabController(
      length: _entityTypes.length,
      vsync: this,
    );
    
    // 设置初始选中的tab
    if (widget.selectedType != null) {
      final index = _entityTypes.indexOf(widget.selectedType!);
      if (index != -1) {
        _tabController.index = index;
      }
    }

    _tabController.addListener(_onTabChanged);
    
    // 初始加载数据
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadEntities();
    });
  }

  @override
  void dispose() {
    _tabController.removeListener(_onTabChanged);
    _tabController.dispose();
    super.dispose();
  }

  void _onTabChanged() {
    final selectedType = _entityTypes[_tabController.index];
    _loadEntities(type: selectedType == 'all' ? null : selectedType);
  }

  void _loadEntities({String? type}) {
    ref.read(entityListProvider.notifier).loadEntities(
      type: type,
      refresh: true,
    );
  }

  @override
  Widget build(BuildContext context) {
    final entityListState = ref.watch(entityListProvider);

    return CollapsibleCard(
      title: '智能实体分析',
      subtitle: '已识别并分析的数据实体',
      trailing: _buildRefreshButton(),
      child: Column(
        children: [
          // 类型选择标签页
          if (widget.showAllTypes)
            Container(
              height: 48,
              child: TabBar(
                controller: _tabController,
                isScrollable: true,
                tabs: _entityTypes.map((type) => Tab(
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(_typeIcons[type], size: 16),
                      const SizedBox(width: 6),
                      Text(_typeLabels[type] ?? type),
                    ],
                  ),
                )).toList(),
              ),
            ),
          
          const SizedBox(height: 16),

          // 实体列表
          _buildEntityList(context, entityListState),
        ],
      ),
    );
  }

  Widget _buildRefreshButton() {
    return IconButton(
      icon: const Icon(Icons.refresh),
      onPressed: () => _loadEntities(),
      tooltip: '刷新数据',
    );
  }

  Widget _buildEntityList(BuildContext context, EntityListState state) {
    if (state.isLoading) {
      return const SizedBox(
        height: 200,
        child: Center(child: CircularProgressIndicator()),
      );
    }

    if (state.error != null) {
      return Container(
        height: 200,
        alignment: Alignment.center,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 48,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(height: 12),
            Text(
              '加载失败',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            Text(
              state.error!,
              style: Theme.of(context).textTheme.bodySmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => _loadEntities(),
              child: const Text('重试'),
            ),
          ],
        ),
      );
    }

    if (state.entities.isEmpty) {
      return Container(
        height: 200,
        alignment: Alignment.center,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.search_off,
              size: 48,
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
            const SizedBox(height: 12),
            Text(
              '暂无数据',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            Text(
              '当前筛选条件下没有找到实体',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      );
    }

    return Container(
      constraints: const BoxConstraints(maxHeight: 600),
      child: ListView.separated(
        shrinkWrap: true,
        itemCount: state.entities.length,
        separatorBuilder: (context, index) => const SizedBox(height: 8),
        itemBuilder: (context, index) {
          final entity = state.entities[index];
          return EntityCard(entity: entity);
        },
      ),
    );
  }
}

/// 实体卡片
class EntityCard extends StatelessWidget {
  final EntityDetail entity;

  const EntityCard({
    super.key,
    required this.entity,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Card(
      elevation: 0,
      margin: EdgeInsets.zero,
      color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
      child: InkWell(
        onTap: () => _showEntityDetails(context),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  // 类型图标
                  Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: _getTypeColor(entity.type).withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Icon(
                      _getTypeIcon(entity.type),
                      size: 16,
                      color: _getTypeColor(entity.type),
                    ),
                  ),
                  const SizedBox(width: 12),
                  
                  // 类型标签
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: _getTypeColor(entity.type).withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      _getTypeLabel(entity.type),
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: _getTypeColor(entity.type),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                  
                  const Spacer(),
                  
                  // 访问次数
                  if (entity.accessCount > 0)
                    Text(
                      '${entity.accessCount}次访问',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: colorScheme.onSurfaceVariant,
                      ),
                    ),
                ],
              ),
              
              const SizedBox(height: 12),
              
              // 实体名称
              Text(
                entity.name,
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w500,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              
              // 描述
              if (entity.description != null) ...[
                const SizedBox(height: 8),
                Text(
                  entity.description!,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
              
              const SizedBox(height: 12),
              
              // 底部信息
              Row(
                children: [
                  // 时间信息
                  Icon(
                    Icons.access_time,
                    size: 14,
                    color: colorScheme.onSurfaceVariant,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    _formatDateTime(entity.createdAt),
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
                  ),
                  
                  const Spacer(),
                  
                  // 操作按钮
                  _buildActionButtons(context),
                ],
              ),
              
              // 标签
              if (entity.tags.isNotEmpty) ...[
                const SizedBox(height: 8),
                Wrap(
                  spacing: 6,
                  runSpacing: 4,
                  children: entity.tags.take(3).map((tag) => Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: colorScheme.outline.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      tag,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: colorScheme.onSurfaceVariant,
                      ),
                    ),
                  )).toList(),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildActionButtons(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        IconButton(
          icon: const Icon(Icons.copy, size: 16),
          onPressed: () => _copyToClipboard(context),
          tooltip: '复制',
          visualDensity: VisualDensity.compact,
        ),
        IconButton(
          icon: const Icon(Icons.open_in_new, size: 16),
          onPressed: () => _openEntity(context),
          tooltip: '打开',
          visualDensity: VisualDensity.compact,
        ),
      ],
    );
  }

  void _copyToClipboard(BuildContext context) {
    Clipboard.setData(ClipboardData(text: entity.name));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('已复制到剪贴板')),
    );
  }

  void _openEntity(BuildContext context) {
    // TODO: 实现打开实体的逻辑
    AppLogger.info('打开实体: ${entity.name}', module: 'EntityCard');
  }

  void _showEntityDetails(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => EntityDetailDialog(entity: entity),
    );
  }

  IconData _getTypeIcon(String type) {
    switch (type) {
      case 'url':
        return Icons.link;
      case 'file_path':
        return Icons.folder;
      case 'email':
        return Icons.email;
      case 'phone':
        return Icons.phone;
      case 'keyword':
        return Icons.tag;
      default:
        return Icons.help_outline;
    }
  }

  Color _getTypeColor(String type) {
    switch (type) {
      case 'url':
        return Colors.blue;
      case 'file_path':
        return Colors.green;
      case 'email':
        return Colors.orange;
      case 'phone':
        return Colors.red;
      case 'keyword':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  String _getTypeLabel(String type) {
    switch (type) {
      case 'url':
        return 'URL';
      case 'file_path':
        return '文件路径';
      case 'email':
        return '邮箱';
      case 'phone':
        return '电话';
      case 'keyword':
        return '关键词';
      default:
        return type.toUpperCase();
    }
  }

  String _formatDateTime(DateTime? dateTime) {
    if (dateTime == null) return '未知时间';
    
    final now = DateTime.now();
    final difference = now.difference(dateTime);
    
    if (difference.inMinutes < 1) {
      return '刚刚';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}分钟前';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}小时前';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}天前';
    } else {
      return '${dateTime.month}/${dateTime.day}';
    }
  }
}

/// 实体详情对话框
class EntityDetailDialog extends StatelessWidget {
  final EntityDetail entity;

  const EntityDetailDialog({
    super.key,
    required this.entity,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Dialog(
      child: Container(
        width: 500,
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  '实体详情',
                  style: theme.textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const Spacer(),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.of(context).pop(),
                ),
              ],
            ),
            
            const SizedBox(height: 20),
            
            // 实体信息
            _buildDetailItem('名称', entity.name),
            _buildDetailItem('类型', entity.type),
            if (entity.description != null)
              _buildDetailItem('描述', entity.description!),
            _buildDetailItem('创建时间', entity.createdAt?.toString() ?? '未知'),
            _buildDetailItem('访问次数', entity.accessCount.toString()),
            
            // 标签
            if (entity.tags.isNotEmpty) ...[
              const SizedBox(height: 16),
              Text(
                '标签',
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: entity.tags.map((tag) => Chip(
                  label: Text(tag),
                  backgroundColor: theme.colorScheme.surfaceContainerHighest,
                )).toList(),
              ),
            ],
            
            const SizedBox(height: 24),
            
            // 操作按钮
            Row(
              children: [
                const Spacer(),
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('关闭'),
                ),
                const SizedBox(width: 12),
                ElevatedButton(
                  onPressed: () {
                    Clipboard.setData(ClipboardData(text: entity.name));
                    Navigator.of(context).pop();
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('已复制到剪贴板')),
                    );
                  },
                  child: const Text('复制'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: const TextStyle(
              fontWeight: FontWeight.w500,
              fontSize: 12,
            ),
          ),
          const SizedBox(height: 4),
          SelectableText(
            value,
            style: const TextStyle(fontSize: 14),
          ),
        ],
      ),
    );
  }
}