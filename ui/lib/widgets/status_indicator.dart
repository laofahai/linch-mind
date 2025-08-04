import 'package:flutter/material.dart';

class StatusIndicator extends StatefulWidget {
  final bool isConnected;
  final VoidCallback? onTap;
  final String? customMessage;

  const StatusIndicator({
    super.key,
    required this.isConnected,
    this.onTap,
    this.customMessage,
  });

  @override
  State<StatusIndicator> createState() => _StatusIndicatorState();
}

class _StatusIndicatorState extends State<StatusIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    _pulseAnimation = Tween<double>(
      begin: 0.8,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));

    if (widget.isConnected) {
      _animationController.repeat(reverse: true);
    }
  }

  @override
  void didUpdateWidget(StatusIndicator oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isConnected && !oldWidget.isConnected) {
      _animationController.repeat(reverse: true);
    } else if (!widget.isConnected && oldWidget.isConnected) {
      _animationController.stop();
      _animationController.reset();
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final statusColor = widget.isConnected 
        ? Colors.green 
        : Colors.red;
    
    final statusText = widget.customMessage ?? 
        (widget.isConnected ? 'Connected' : 'Disconnected');
    
    final statusIcon = widget.isConnected 
        ? Icons.cloud_done 
        : Icons.cloud_off;

    return GestureDetector(
      onTap: widget.onTap,
      child: Tooltip(
        message: statusText,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: statusColor.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: statusColor.withValues(alpha: 0.3),
              width: 1,
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              AnimatedBuilder(
                animation: _pulseAnimation,
                builder: (context, child) {
                  return Transform.scale(
                    scale: widget.isConnected ? _pulseAnimation.value : 1.0,
                    child: Icon(
                      statusIcon,
                      size: 16,
                      color: statusColor,
                    ),
                  );
                },
              ),
              const SizedBox(width: 6),
              Text(
                statusText,
                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                  color: statusColor,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// 简化版状态点
class StatusDot extends StatelessWidget {
  final bool isActive;
  final Color? activeColor;
  final Color? inactiveColor;
  final double size;

  const StatusDot({
    super.key,
    required this.isActive,
    this.activeColor,
    this.inactiveColor,
    this.size = 8.0,
  });

  @override
  Widget build(BuildContext context) {
    final active = activeColor ?? Colors.green;
    final inactive = inactiveColor ?? Colors.grey;

    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: isActive ? active : inactive,
        shape: BoxShape.circle,
        boxShadow: isActive ? [
          BoxShadow(
            color: active.withValues(alpha: 0.5),
            blurRadius: 4,
            spreadRadius: 1,
          ),
        ] : null,
      ),
    );
  }
}

// 详细状态卡片
class StatusCard extends StatelessWidget {
  final String title;
  final bool isHealthy;
  final String? errorMessage;
  final String? lastUpdateTime;
  final VoidCallback? onRetry;
  final VoidCallback? onViewDetails;

  const StatusCard({
    super.key,
    required this.title,
    required this.isHealthy,
    this.errorMessage,
    this.lastUpdateTime,
    this.onRetry,
    this.onViewDetails,
  });

  @override
  Widget build(BuildContext context) {
    final statusColor = isHealthy ? Colors.green : Colors.red;
    final statusIcon = isHealthy ? Icons.check_circle : Icons.error;
    final statusText = isHealthy ? 'Healthy' : 'Error';

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 标题行
            Row(
              children: [
                Expanded(
                  child: Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: statusColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        statusIcon,
                        size: 14,
                        color: statusColor,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        statusText,
                        style: Theme.of(context).textTheme.labelSmall?.copyWith(
                          color: statusColor,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),

            if (!isHealthy && errorMessage != null) ...[
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.withValues(alpha: 0.05),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: Colors.red.withValues(alpha: 0.2),
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.warning,
                      size: 16,
                      color: Colors.red,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        errorMessage!,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.red,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],

            if (lastUpdateTime != null) ...[
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(
                    Icons.access_time,
                    size: 14,
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    'Last updated: $lastUpdateTime',
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ],

            // 操作按钮
            if (onRetry != null || onViewDetails != null) ...[
              const SizedBox(height: 12),
              Row(
                children: [
                  if (onRetry != null)
                    TextButton.icon(
                      onPressed: onRetry,
                      icon: const Icon(Icons.refresh, size: 16),
                      label: const Text('Retry'),
                      style: TextButton.styleFrom(
                        visualDensity: VisualDensity.compact,
                      ),
                    ),
                  if (onViewDetails != null) ...[
                    if (onRetry != null) const SizedBox(width: 8),
                    TextButton.icon(
                      onPressed: onViewDetails,
                      icon: const Icon(Icons.info_outline, size: 16),
                      label: const Text('Details'),
                      style: TextButton.styleFrom(
                        visualDensity: VisualDensity.compact,
                      ),
                    ),
                  ],
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}