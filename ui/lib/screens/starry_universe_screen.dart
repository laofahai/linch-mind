import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../widgets/starry_universe/starry_universe_widget.dart';

/// 星空宇宙可视化界面
/// 提供连接器数据的震撼宇宙视觉体验
class StarryUniverseScreen extends StatefulWidget {
  const StarryUniverseScreen({super.key});

  @override
  State<StarryUniverseScreen> createState() => _StarryUniverseScreenState();
}

class _StarryUniverseScreenState extends State<StarryUniverseScreen> {
  String _currentMode = 'universe';
  bool _immersiveMode = false;

  @override
  void initState() {
    super.initState();
    // 设置系统UI为沉浸模式，增强宇宙感
    SystemChrome.setSystemUIOverlayStyle(
      const SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarBrightness: Brightness.dark,
        systemNavigationBarColor: Colors.transparent,
        systemNavigationBarIconBrightness: Brightness.light,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF000014), // 深空黑背景
      body: Stack(
        children: [
          // 全屏宇宙可视化
          Positioned.fill(
            child: StarryUniverseWidget(
              initialMode: _currentMode,
              enableInteraction: true,
              showControls: !_immersiveMode,
              onModeChanged: (mode) {
                setState(() {
                  _currentMode = mode;
                });
              },
            ),
          ),

          // 左上角沉浸模式开关
          Positioned(
            top: MediaQuery.of(context).padding.top + 16,
            left: 16,
            child: _buildImmersiveModeToggle(),
          ),
        ],
      ),
    );
  }

  /// 构建沉浸模式切换器
  Widget _buildImmersiveModeToggle() {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.6),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: const Color(0xFFFFD700).withValues(alpha: 0.4),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.5),
            blurRadius: 6,
            spreadRadius: 1,
          ),
        ],
      ),
      child: IconButton(
        onPressed: () {
          setState(() {
            _immersiveMode = !_immersiveMode;
          });
          HapticFeedback.lightImpact();
        },
        icon: Icon(
          _immersiveMode ? Icons.visibility : Icons.visibility_off,
          color: const Color(0xFFFFD700),
          size: 20,
        ),
        tooltip: _immersiveMode ? '显示控制' : '沉浸模式',
      ),
    );
  }
}
