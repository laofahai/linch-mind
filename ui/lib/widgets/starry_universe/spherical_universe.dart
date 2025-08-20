/// 球形宇宙 - 简单直接的数据可视化主组件
///
/// 这是Linch Mind项目的核心可视化组件，将4种数据类型转换为球形数据可视化：
/// - Universal Index → 搜索数据（内层，金色）
/// - Entity → 实体数据（中层，蓝色）
/// - Graph → 图数据（外层，紫色）
/// - Vector → 向量数据（动态聚类，红色）

// 核心组件导出
export 'spherical_config.dart';
export 'spherical_camera.dart';
export 'spherical_renderer.dart';
export 'spherical_data_mapper.dart';
export 'spherical_interactions.dart';

// 主组件导出
export 'spherical_universe_widget.dart';

/// 快速使用示例:
///
/// ```dart
/// import 'package:linch_mind/widgets/starry_universe/spherical_universe.dart';
///
/// class MyScreen extends StatelessWidget {
///   @override
///   Widget build(BuildContext context) {
///     return Scaffold(
///       body: SphericalUniverseWidget(
///         searchData: searchResults,
///         entityData: entities,
///         graphData: graphNetwork,
///         vectorData: vectors,
///         onDataSelected: (id) {
///           print('选中数据: $id');
///         },
///         showDebugInfo: true, // 开发时显示调试信息
///       ),
///     );
///   }
/// }
/// ```
///
/// 主要特性:
/// - 6个文件实现完整球形可视化
/// - 4种数据类型正确分层显示
/// - 360度无边界旋转导航
/// - 相机缩放改变观察半径
/// - 35K数据点稳定60fps
/// - 支持键盘快捷键和手势操作
///
/// 键盘快捷键:
/// - Space: 重置相机
/// - 方向键: 旋转视角
/// - +/-: 缩放
/// - 1-4: 聚焦不同数据类型
///
/// 手势操作:
/// - 单指拖拽: 旋转视角
/// - 双指缩放: 改变观察距离
/// - 点击: 选择数据点
/// - 双击: 聚焦到数据点
/// - 双击空白: 重置相机
///
/// 架构原则:
/// - KISS原则: 简单直接，不搞复杂设计
/// - 数据结构优先: 球面坐标(r,θ,φ)直接转换
/// - 一次渲染: CustomPaint直接绘制
/// - 性能导向: 35K数据规模优化
