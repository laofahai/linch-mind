import 'package:flutter/material.dart';

/// 加载状态包装器 - 提供淡入淡出过渡效果
class LoadingStateWrapper extends StatefulWidget {
  final bool isLoading;
  final Widget loadingWidget;
  final Widget child;
  final Duration animationDuration;
  final Widget? errorWidget;
  final String? error;

  const LoadingStateWrapper({
    super.key,
    required this.isLoading,
    required this.loadingWidget,
    required this.child,
    this.animationDuration = const Duration(milliseconds: 300),
    this.errorWidget,
    this.error,
  });

  @override
  State<LoadingStateWrapper> createState() => _LoadingStateWrapperState();
}

class _LoadingStateWrapperState extends State<LoadingStateWrapper>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeAnimation;
  bool _showingContent = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
    
    _updateShowingContent();
  }

  @override
  void didUpdateWidget(LoadingStateWrapper oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.isLoading != widget.isLoading || 
        oldWidget.error != widget.error) {
      _updateShowingContent();
    }
  }

  void _updateShowingContent() {
    final shouldShowContent = !widget.isLoading && widget.error == null;
    
    if (_showingContent != shouldShowContent) {
      _showingContent = shouldShowContent;
      
      if (_showingContent) {
        _controller.forward();
      } else {
        _controller.reverse();
      }
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // 如果有错误，显示错误widget
    if (widget.error != null && widget.errorWidget != null) {
      return FadeTransition(
        opacity: _fadeAnimation,
        child: widget.errorWidget!,
      );
    }
    
    return AnimatedSwitcher(
      duration: widget.animationDuration,
      child: widget.isLoading || widget.error != null
          ? widget.loadingWidget
          : FadeTransition(
              opacity: _fadeAnimation,
              child: widget.child,
            ),
    );
  }
}

/// 错误恢复组件
class ErrorRecoveryWidget extends StatelessWidget {
  final String error;
  final VoidCallback? onRetry;
  final String? retryLabel;
  final IconData? icon;

  const ErrorRecoveryWidget({
    super.key,
    required this.error,
    this.onRetry,
    this.retryLabel = '重试',
    this.icon = Icons.error_outline,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Center(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                icon,
                size: 48,
                color: theme.colorScheme.error,
              ),
              const SizedBox(height: 16),
              Text(
                '加载失败',
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                error,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
                textAlign: TextAlign.center,
              ),
              if (onRetry != null) ...[
                const SizedBox(height: 16),
                FilledButton.icon(
                  onPressed: onRetry,
                  icon: const Icon(Icons.refresh),
                  label: Text(retryLabel!),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

/// 渐变过渡包装器
class FadeTransitionWrapper extends StatefulWidget {
  final Widget child;
  final Duration duration;
  final bool show;

  const FadeTransitionWrapper({
    super.key,
    required this.child,
    this.duration = const Duration(milliseconds: 300),
    this.show = true,
  });

  @override
  State<FadeTransitionWrapper> createState() => _FadeTransitionWrapperState();
}

class _FadeTransitionWrapperState extends State<FadeTransitionWrapper>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );
    _animation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
    
    if (widget.show) {
      _controller.forward();
    }
  }

  @override
  void didUpdateWidget(FadeTransitionWrapper oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.show != widget.show) {
      if (widget.show) {
        _controller.forward();
      } else {
        _controller.reverse();
      }
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _animation,
      child: widget.child,
    );
  }
}

/// 滑动过渡包装器
class SlideTransitionWrapper extends StatefulWidget {
  final Widget child;
  final Duration duration;
  final bool show;
  final Offset beginOffset;
  final Offset endOffset;

  const SlideTransitionWrapper({
    super.key,
    required this.child,
    this.duration = const Duration(milliseconds: 400),
    this.show = true,
    this.beginOffset = const Offset(0, 0.1),
    this.endOffset = Offset.zero,
  });

  @override
  State<SlideTransitionWrapper> createState() => _SlideTransitionWrapperState();
}

class _SlideTransitionWrapperState extends State<SlideTransitionWrapper>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );
    _slideAnimation = Tween<Offset>(
      begin: widget.beginOffset,
      end: widget.endOffset,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOutCubic,
    ));
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
    
    if (widget.show) {
      _controller.forward();
    }
  }

  @override
  void didUpdateWidget(SlideTransitionWrapper oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.show != widget.show) {
      if (widget.show) {
        _controller.forward();
      } else {
        _controller.reverse();
      }
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SlideTransition(
      position: _slideAnimation,
      child: FadeTransition(
        opacity: _fadeAnimation,
        child: widget.child,
      ),
    );
  }
}

/// 弹性过渡包装器
class ScaleTransitionWrapper extends StatefulWidget {
  final Widget child;
  final Duration duration;
  final bool show;
  final double beginScale;
  final double endScale;

  const ScaleTransitionWrapper({
    super.key,
    required this.child,
    this.duration = const Duration(milliseconds: 250),
    this.show = true,
    this.beginScale = 0.8,
    this.endScale = 1.0,
  });

  @override
  State<ScaleTransitionWrapper> createState() => _ScaleTransitionWrapperState();
}

class _ScaleTransitionWrapperState extends State<ScaleTransitionWrapper>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );
    _scaleAnimation = Tween<double>(
      begin: widget.beginScale,
      end: widget.endScale,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.elasticOut,
    ));
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
    
    if (widget.show) {
      _controller.forward();
    }
  }

  @override
  void didUpdateWidget(ScaleTransitionWrapper oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.show != widget.show) {
      if (widget.show) {
        _controller.forward();
      } else {
        _controller.reverse();
      }
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ScaleTransition(
      scale: _scaleAnimation,
      child: FadeTransition(
        opacity: _fadeAnimation,
        child: widget.child,
      ),
    );
  }
}