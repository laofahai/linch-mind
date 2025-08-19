/// 星空数据可视化系统 - 统一导出文件
/// 
/// 这是Linch Mind项目的核心可视化组件，将4种数据类型转换为沉浸式的星空体验：
/// - Universal Index → 搜索星河 🌊
/// - Entity → 智慧星座 ⭐  
/// - Graph → 知识宇宙 🌌
/// - Vector → 相似星云 💫
///
/// 技术特性：
/// - 高性能粒子系统 (5000+粒子 60fps)
/// - 自适应质量管理 (LOD + 性能监控)
/// - IPC数据源集成
/// - 响应式动画系统
/// - 空间索引优化

// 核心组件
export 'core/cosmic_theme.dart';
export 'core/starry_canvas.dart';
export 'core/particle_system.dart';
export 'core/cosmic_animations.dart';
export 'core/data_mappers.dart';
export 'core/performance_optimizer.dart';

// 状态管理
export 'providers/starry_universe_provider.dart';

// 主要组件
export 'starry_universe_widget.dart';
export 'starry_universe_demo.dart';

/// 快速使用示例:
/// 
/// ```dart
/// import 'package:linch_mind/widgets/starry_universe/starry_universe.dart';
/// 
/// class MyApp extends StatelessWidget {
///   @override
///   Widget build(BuildContext context) {
///     return ProviderScope(
///       child: MaterialApp(
///         home: Scaffold(
///           body: StarryUniverseWidget(
///             initialMode: 'search',
///             onModeChanged: (mode) => print('Mode changed to: $mode'),
///             onObjectSelected: (obj) => print('Selected: ${obj.id}'),
///           ),
///         ),
///       ),
///     );
///   }
/// }
/// ```
/// 
/// 性能建议:
/// - 在低端设备上使用 PerformanceLevel.medium 或更低
/// - 启用自适应质量管理以自动优化性能
/// - 使用空间索引进行大数据集可视化
/// - 定期清理粒子缓存以避免内存泄漏
/// 
/// 架构说明:
/// - 遵循Linch Mind的IPC架构约束
/// - 使用ServiceFacade模式获取服务
/// - 集成现有的Riverpod状态管理
/// - 支持实时数据更新和动画响应