import 'package:flutter/material.dart';
import '../../providers/mode_switch_provider.dart';

/// 模式切换动画器
class ModeTransitionAnimator extends StatefulWidget {
  final AppMode currentMode;
  final bool isTransitioning;
  final Widget child;

  const ModeTransitionAnimator({
    super.key,
    required this.currentMode,
    required this.isTransitioning,
    required this.child,
  });

  @override
  State<ModeTransitionAnimator> createState() => _ModeTransitionAnimatorState();
}

class _ModeTransitionAnimatorState extends State<ModeTransitionAnimator>
    with TickerProviderStateMixin {
  late AnimationController _colorController;
  late AnimationController _scaleController;
  late AnimationController _fadeController;

  late Animation<Color?> _colorAnimation;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;

  AppMode? _previousMode;

  @override
  void initState() {
    super.initState();

    _colorController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    _scaleController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );

    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 400),
      vsync: this,
    );

    _setupAnimations();
    _previousMode = widget.currentMode;
  }

  void _setupAnimations() {
    _colorAnimation = ColorTween(
      begin: _previousMode?.color ?? widget.currentMode.color,
      end: widget.currentMode.color,
    ).animate(CurvedAnimation(
      parent: _colorController,
      curve: Curves.easeInOutCubic,
    ));

    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 1.05,
    ).animate(CurvedAnimation(
      parent: _scaleController,
      curve: Curves.elasticOut,
    ));

    _fadeAnimation = Tween<double>(
      begin: 1.0,
      end: 0.8,
    ).animate(CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void didUpdateWidget(ModeTransitionAnimator oldWidget) {
    super.didUpdateWidget(oldWidget);

    // 检测模式变化
    if (oldWidget.currentMode != widget.currentMode) {
      _previousMode = oldWidget.currentMode;
      _updateColorAnimation();
      _colorController.forward();
    }

    // 检测切换状态变化
    if (oldWidget.isTransitioning != widget.isTransitioning) {
      if (widget.isTransitioning) {
        _startTransitionAnimation();
      } else {
        _endTransitionAnimation();
      }
    }
  }

  void _updateColorAnimation() {
    _colorAnimation = ColorTween(
      begin: _previousMode?.color ?? widget.currentMode.color,
      end: widget.currentMode.color,
    ).animate(CurvedAnimation(
      parent: _colorController,
      curve: Curves.easeInOutCubic,
    ));
  }

  void _startTransitionAnimation() {
    _scaleController.forward();
    _fadeController.forward();
  }

  void _endTransitionAnimation() {
    _scaleController.reverse();
    _fadeController.reverse();
  }

  @override
  void dispose() {
    _colorController.dispose();
    _scaleController.dispose();
    _fadeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: Listenable.merge([
        _colorController,
        _scaleController,
        _fadeController,
      ]),
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: Opacity(
            opacity: _fadeAnimation.value,
            child: Container(
              decoration: BoxDecoration(
                boxShadow: [
                  if (widget.isTransitioning)
                    BoxShadow(
                      color: (_colorAnimation.value ?? widget.currentMode.color)
                          .withValues(alpha: 0.3),
                      blurRadius: 20,
                      spreadRadius: 2,
                    ),
                ],
              ),
              child: widget.child,
            ),
          ),
        );
      },
    );
  }
}

/// 模式图标动画器
class ModeIconAnimator extends StatefulWidget {
  final AppMode mode;
  final bool isSelected;
  final bool isTransitioning;
  final VoidCallback? onTap;

  const ModeIconAnimator({
    super.key,
    required this.mode,
    required this.isSelected,
    required this.isTransitioning,
    this.onTap,
  });

  @override
  State<ModeIconAnimator> createState() => _ModeIconAnimatorState();
}

class _ModeIconAnimatorState extends State<ModeIconAnimator>
    with TickerProviderStateMixin {
  late AnimationController _pulseController;
  late AnimationController _bounceController;

  late Animation<double> _pulseAnimation;
  late Animation<double> _bounceAnimation;

  @override
  void initState() {
    super.initState();

    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );

    _bounceController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );

    _pulseAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));

    _bounceAnimation = Tween<double>(
      begin: 1.0,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _bounceController,
      curve: Curves.elasticOut,
    ));

    if (widget.isSelected) {
      _pulseController.repeat(reverse: true);
    }
  }

  @override
  void didUpdateWidget(ModeIconAnimator oldWidget) {
    super.didUpdateWidget(oldWidget);

    if (oldWidget.isSelected != widget.isSelected) {
      if (widget.isSelected) {
        _pulseController.repeat(reverse: true);
        _bounceController.forward().then((_) {
          _bounceController.reverse();
        });
      } else {
        _pulseController.stop();
        _pulseController.reset();
      }
    }
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _bounceController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return GestureDetector(
      onTap: widget.onTap,
      child: AnimatedBuilder(
        animation: Listenable.merge([_pulseController, _bounceController]),
        builder: (context, child) {
          return Transform.scale(
            scale: _bounceAnimation.value,
            child: Container(
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                boxShadow: widget.isSelected
                    ? [
                        BoxShadow(
                          color: widget.mode.color.withValues(
                            alpha: 0.3 * _pulseAnimation.value,
                          ),
                          blurRadius: 20 * _pulseAnimation.value,
                          spreadRadius: 5 * _pulseAnimation.value,
                        ),
                      ]
                    : null,
              ),
              child: Icon(
                widget.mode.icon,
                color: widget.isSelected
                    ? widget.mode.color
                    : theme.colorScheme.onSurfaceVariant,
                size: 20,
              ),
            ),
          );
        },
      ),
    );
  }
}

/// 模式切换进度指示器
class ModeTransitionProgress extends StatefulWidget {
  final bool isTransitioning;
  final AppMode currentMode;

  const ModeTransitionProgress({
    super.key,
    required this.isTransitioning,
    required this.currentMode,
  });

  @override
  State<ModeTransitionProgress> createState() => _ModeTransitionProgressState();
}

class _ModeTransitionProgressState extends State<ModeTransitionProgress>
    with TickerProviderStateMixin {
  late AnimationController _progressController;
  late Animation<double> _progressAnimation;

  @override
  void initState() {
    super.initState();

    _progressController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    _progressAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _progressController,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void didUpdateWidget(ModeTransitionProgress oldWidget) {
    super.didUpdateWidget(oldWidget);

    if (oldWidget.isTransitioning != widget.isTransitioning) {
      if (widget.isTransitioning) {
        _progressController.forward();
      } else {
        _progressController.reverse();
      }
    }
  }

  @override
  void dispose() {
    _progressController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.isTransitioning) {
      return const SizedBox.shrink();
    }

    return AnimatedBuilder(
      animation: _progressAnimation,
      builder: (context, child) {
        return Container(
          margin: const EdgeInsets.symmetric(vertical: 8),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              LinearProgressIndicator(
                value: _progressAnimation.value,
                backgroundColor:
                    widget.currentMode.color.withValues(alpha: 0.2),
                valueColor: AlwaysStoppedAnimation(widget.currentMode.color),
              ),
              const SizedBox(height: 4),
              Text(
                '正在切换到${widget.currentMode.displayName}模式...',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: widget.currentMode.color,
                      fontStyle: FontStyle.italic,
                    ),
              ),
            ],
          ),
        );
      },
    );
  }
}
