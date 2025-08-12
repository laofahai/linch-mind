import 'package:flutter/material.dart';

/// 骨架屏基础样式配置
class SkeletonTheme {
  static const Duration shimmerDuration = Duration(milliseconds: 1500);
  static const double borderRadius = 8.0;
  static const double smallBorderRadius = 4.0;
  
  static Color baseColor(BuildContext context) => 
    Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.3);
    
  static Color highlightColor(BuildContext context) => 
    Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.6);
}

/// 基础骨架盒子组件
class SkeletonBox extends StatefulWidget {
  final double? width;
  final double? height;
  final BorderRadius? borderRadius;
  final EdgeInsetsGeometry? margin;

  const SkeletonBox({
    super.key,
    this.width,
    this.height,
    this.borderRadius,
    this.margin,
  });

  @override
  State<SkeletonBox> createState() => _SkeletonBoxState();
}

class _SkeletonBoxState extends State<SkeletonBox>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: SkeletonTheme.shimmerDuration,
      vsync: this,
    );
    _animation = Tween<double>(begin: -1.0, end: 2.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.linear),
    );
    _controller.repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final borderRadius = widget.borderRadius ?? 
      BorderRadius.circular(SkeletonTheme.borderRadius);

    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Container(
          width: widget.width,
          height: widget.height,
          margin: widget.margin,
          decoration: BoxDecoration(
            borderRadius: borderRadius,
            gradient: LinearGradient(
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
              stops: [
                (_animation.value - 0.5).clamp(0.0, 1.0),
                _animation.value.clamp(0.0, 1.0),
                (_animation.value + 0.5).clamp(0.0, 1.0),
              ],
              colors: [
                SkeletonTheme.baseColor(context),
                SkeletonTheme.highlightColor(context),
                SkeletonTheme.baseColor(context),
              ],
            ),
          ),
        );
      },
    );
  }
}

/// 文本行骨架
class SkeletonText extends StatelessWidget {
  final double? width;
  final double height;
  final EdgeInsetsGeometry? margin;

  const SkeletonText({
    super.key,
    this.width,
    this.height = 14.0,
    this.margin,
  });

  /// 创建多行文本骨架
  static Widget multiLine({
    required int lines,
    double? firstLineWidth,
    double? otherLinesWidth,
    double height = 14.0,
    double spacing = 8.0,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: List.generate(lines, (index) {
        double? lineWidth;
        if (index == 0 && firstLineWidth != null) {
          lineWidth = firstLineWidth;
        } else if (index > 0 && otherLinesWidth != null) {
          lineWidth = otherLinesWidth;
        }
        
        return SkeletonText(
          width: lineWidth,
          height: height,
          margin: index < lines - 1 ? EdgeInsets.only(bottom: spacing) : null,
        );
      }),
    );
  }

  @override
  Widget build(BuildContext context) {
    return SkeletonBox(
      width: width,
      height: height,
      margin: margin,
      borderRadius: BorderRadius.circular(SkeletonTheme.smallBorderRadius),
    );
  }
}

/// 卡片骨架
class SkeletonCard extends StatelessWidget {
  final double? width;
  final double? height;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final Widget? child;

  const SkeletonCard({
    super.key,
    this.width,
    this.height,
    this.padding = const EdgeInsets.all(16),
    this.margin,
    this.child,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: margin,
      child: Container(
        width: width,
        height: height,
        padding: padding,
        child: child,
      ),
    );
  }
}

/// 圆形骨架（用于头像等）
class SkeletonCircle extends StatelessWidget {
  final double size;
  final EdgeInsetsGeometry? margin;

  const SkeletonCircle({
    super.key,
    required this.size,
    this.margin,
  });

  @override
  Widget build(BuildContext context) {
    return SkeletonBox(
      width: size,
      height: size,
      margin: margin,
      borderRadius: BorderRadius.circular(size / 2),
    );
  }
}

/// 图表骨架
class SkeletonChart extends StatelessWidget {
  final double? width;
  final double height;
  final EdgeInsetsGeometry? margin;

  const SkeletonChart({
    super.key,
    this.width,
    this.height = 120.0,
    this.margin,
  });

  @override
  Widget build(BuildContext context) {
    return SkeletonCard(
      width: width,
      height: height,
      margin: margin,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SkeletonText(width: 120, height: 16),
          const SizedBox(height: 16),
          Expanded(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: List.generate(6, (index) {
                final heights = [0.3, 0.7, 0.5, 0.9, 0.4, 0.6];
                return Expanded(
                  child: Container(
                    margin: const EdgeInsets.symmetric(horizontal: 2),
                    child: SkeletonBox(
                      height: (height - 60) * heights[index],
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                );
              }),
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: List.generate(3, (index) => 
              Expanded(
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    SkeletonBox(width: 12, height: 12, 
                      borderRadius: BorderRadius.circular(6)),
                    const SizedBox(width: 6),
                    const Flexible(child: SkeletonText(height: 12)),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// 列表项骨架
class SkeletonListItem extends StatelessWidget {
  final bool hasAvatar;
  final bool hasSubtitle;
  final EdgeInsetsGeometry? margin;

  const SkeletonListItem({
    super.key,
    this.hasAvatar = false,
    this.hasSubtitle = true,
    this.margin,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: margin,
      child: Row(
        children: [
          if (hasAvatar) ...[
            const SkeletonCircle(size: 40),
            const SizedBox(width: 12),
          ],
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SkeletonText(width: 200, height: 16),
                if (hasSubtitle) ...[
                  const SizedBox(height: 6),
                  const SkeletonText(width: 150, height: 14),
                ],
              ],
            ),
          ),
          const SizedBox(width: 12),
          const SkeletonBox(width: 24, height: 24),
        ],
      ),
    );
  }
}