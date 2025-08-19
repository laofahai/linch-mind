/// 优化的粒子系统 - 高性能星空效果渲染
import 'dart:math' as math;
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:vector_math/vector_math.dart' as vm;
import 'cosmic_theme.dart';

/// 单个粒子的数据结构
class Particle {
  vm.Vector2 position;
  vm.Vector2 velocity;
  Color color;
  double size;
  double intensity;
  double lifetime;
  double maxLifetime;
  String? dataId; // 关联的数据ID
  
  Particle({
    required this.position,
    required this.velocity,
    required this.color,
    required this.size,
    required this.intensity,
    required this.lifetime,
    required this.maxLifetime,
    this.dataId,
  });
  
  /// 更新粒子状态
  void update(double deltaTime) {
    // 更新位置
    position += velocity * deltaTime;
    
    // 更新生命周期
    lifetime -= deltaTime;
    
    // 根据生命周期调整透明度
    final lifeRatio = lifetime / maxLifetime;
    intensity = (lifeRatio * 0.8 + 0.2).clamp(0.0, 1.0);
  }
  
  /// 检查粒子是否死亡
  bool get isDead => lifetime <= 0;
  
  /// 重置粒子到初始状态
  void reset(vm.Vector2 newPosition, vm.Vector2 newVelocity, Color newColor) {
    position = newPosition;
    velocity = newVelocity;
    color = newColor;
    lifetime = maxLifetime;
    intensity = 1.0;
  }
  
  /// 应用引力场效果
  void applyGravity(vm.Vector2 center, double strength) {
    final direction = center - position;
    final distance = direction.length;
    if (distance > 0) {
      final force = direction.normalized() * (strength / (distance * distance + 1));
      velocity += force;
    }
  }
}

/// 粒子池 - 对象重用以减少GC压力
class ParticlePool {
  final List<Particle> _pool = [];
  final int maxSize;
  
  ParticlePool({this.maxSize = 1000});
  
  /// 获取一个粒子实例
  Particle acquire() {
    if (_pool.isNotEmpty) {
      return _pool.removeLast();
    }
    return Particle(
      position: vm.Vector2.zero(),
      velocity: vm.Vector2.zero(),
      color: Colors.white,
      size: 2.0,
      intensity: 1.0,
      lifetime: 5.0,
      maxLifetime: 5.0,
    );
  }
  
  /// 释放粒子实例回池中
  void release(Particle particle) {
    if (_pool.length < maxSize) {
      _pool.add(particle);
    }
  }
}

/// 优化的粒子系统
class OptimizedParticleSystem {
  final List<Particle> _particles = [];
  final ParticlePool _pool = ParticlePool();
  final math.Random _random = math.Random();
  
  // 配置参数
  int maxParticles;
  double spawnRate;
  vm.Vector2? gravityCenter;
  double gravityStrength;
  Size? bounds;
  
  // 性能统计
  int _frameCount = 0;
  double _lastFPS = 60.0;
  int get particleCount => _particles.length;
  double get fps => _lastFPS;
  
  OptimizedParticleSystem({
    this.maxParticles = 1000,
    this.spawnRate = 50.0, // 每秒生成粒子数
    this.gravityStrength = 100.0,
  });
  
  /// 更新所有粒子
  void update(double deltaTime) {
    _frameCount++;
    if (_frameCount % 60 == 0) {
      _lastFPS = 60.0 / deltaTime; // 粗略计算FPS
    }
    
    // 更新现有粒子
    for (int i = _particles.length - 1; i >= 0; i--) {
      final particle = _particles[i];
      particle.update(deltaTime);
      
      // 应用引力场
      if (gravityCenter != null) {
        particle.applyGravity(gravityCenter!, gravityStrength * deltaTime);
      }
      
      // 边界检查
      if (bounds != null) {
        _applyBoundaryConditions(particle, bounds!);
      }
      
      // 移除死亡粒子
      if (particle.isDead) {
        _particles.removeAt(i);
        _pool.release(particle);
      }
    }
    
    // 生成新粒子
    if (_particles.length < maxParticles) {
      final particlesToSpawn = (spawnRate * deltaTime).round();
      for (int i = 0; i < particlesToSpawn && _particles.length < maxParticles; i++) {
        _spawnParticle();
      }
    }
  }
  
  /// 生成新粒子
  void _spawnParticle() {
    if (bounds == null) return;
    
    final particle = _pool.acquire();
    
    // 随机位置
    final x = _random.nextDouble() * bounds!.width;
    final y = _random.nextDouble() * bounds!.height;
    
    // 随机速度
    final vx = (_random.nextDouble() - 0.5) * 20;
    final vy = (_random.nextDouble() - 0.5) * 20;
    
    // 随机颜色和属性
    final colors = [
      CosmicTheme.starGold,
      CosmicTheme.starBlue,
      CosmicTheme.starPurple,
      CosmicTheme.starWhite,
    ];
    final color = colors[_random.nextInt(colors.length)];
    
    particle.reset(
      vm.Vector2(x, y),
      vm.Vector2(vx, vy),
      color,
    );
    
    particle.size = _random.nextDouble() * 3 + 1;
    particle.lifetime = particle.maxLifetime = _random.nextDouble() * 8 + 2;
    
    _particles.add(particle);
  }
  
  /// 应用边界条件
  void _applyBoundaryConditions(Particle particle, Size bounds) {
    // 环绕边界
    if (particle.position.x < 0) {
      particle.position.x = bounds.width;
    } else if (particle.position.x > bounds.width) {
      particle.position.x = 0;
    }
    
    if (particle.position.y < 0) {
      particle.position.y = bounds.height;
    } else if (particle.position.y > bounds.height) {
      particle.position.y = 0;
    }
  }
  
  /// 设置边界
  void setBounds(Size newBounds) {
    bounds = newBounds;
  }
  
  /// 设置引力中心
  void setGravityCenter(vm.Vector2? center) {
    gravityCenter = center;
  }
  
  /// 添加数据驱动的粒子
  void addDataParticle({
    required vm.Vector2 position,
    required String dataId,
    required String dataType,
    double? score,
  }) {
    if (_particles.length >= maxParticles) return;
    
    final particle = _pool.acquire();
    final color = CosmicTheme.getStarColor(dataType);
    final scoreBasedColor = score != null 
        ? CosmicTheme.getScoreBasedColor(color, score)
        : color;
    
    particle.reset(
      position,
      vm.Vector2((_random.nextDouble() - 0.5) * 10, (_random.nextDouble() - 0.5) * 10),
      scoreBasedColor,
    );
    
    particle.dataId = dataId;
    particle.size = score != null 
        ? (score * 4 + 2).clamp(2.0, 6.0)
        : 3.0;
    particle.lifetime = particle.maxLifetime = 10.0; // 数据粒子存活更久
    
    _particles.add(particle);
  }
  
  /// 爆发效果 - 生成大量粒子
  void burst(vm.Vector2 center, int count, {Color? color}) {
    for (int i = 0; i < count && _particles.length < maxParticles; i++) {
      final particle = _pool.acquire();
      
      // 径向分布
      final angle = (i / count) * 2 * math.pi;
      final radius = _random.nextDouble() * 50 + 10;
      final position = center + vm.Vector2(
        math.cos(angle) * radius,
        math.sin(angle) * radius,
      );
      
      // 向外扩散的速度
      final velocity = vm.Vector2(
        math.cos(angle) * (_random.nextDouble() * 100 + 50),
        math.sin(angle) * (_random.nextDouble() * 100 + 50),
      );
      
      particle.reset(
        position,
        velocity,
        color ?? CosmicTheme.starGold,
      );
      
      particle.lifetime = particle.maxLifetime = _random.nextDouble() * 3 + 1;
      _particles.add(particle);
    }
  }
  
  /// 清除所有粒子
  void clear() {
    for (final particle in _particles) {
      _pool.release(particle);
    }
    _particles.clear();
  }
  
  /// 获取所有粒子的只读列表
  List<Particle> get particles => List.unmodifiable(_particles);
}

/// 预定义的粒子效果
class ParticleEffects {
  /// 星河流动效果
  static void createStarRiver(OptimizedParticleSystem system, vm.Vector2 start, vm.Vector2 end) {
    const int particleCount = 50;
    for (int i = 0; i < particleCount; i++) {
      final t = i / particleCount;
      final position = start + (end - start) * t;
      
      // 添加随机偏移
      final offset = vm.Vector2(
        (math.Random().nextDouble() - 0.5) * 20,
        (math.Random().nextDouble() - 0.5) * 20,
      );
      final finalPosition = position + offset;
      
      system.addDataParticle(
        position: finalPosition,
        dataId: 'river_$i',
        dataType: 'document',
        score: 1.0 - (t * 0.5), // 起点更亮
      );
    }
  }
  
  /// 星座形成效果
  static void createConstellation(OptimizedParticleSystem system, List<vm.Vector2> points) {
    for (int i = 0; i < points.length; i++) {
      system.addDataParticle(
        position: points[i],
        dataId: 'constellation_$i',
        dataType: 'concept',
        score: 0.8,
      );
    }
  }
  
  /// 星云扩散效果
  static void createNebulaExpansion(OptimizedParticleSystem system, vm.Vector2 center) {
    const int layers = 3;
    const int particlesPerLayer = 20;
    
    for (int layer = 0; layer < layers; layer++) {
      final radius = (layer + 1) * 30.0;
      for (int i = 0; i < particlesPerLayer; i++) {
        final angle = (i / particlesPerLayer) * 2 * math.pi;
        final position = center + vm.Vector2(
          math.cos(angle) * radius,
          math.sin(angle) * radius,
        );
        
        system.addDataParticle(
          position: position,
          dataId: 'nebula_${layer}_$i',
          dataType: 'image',
          score: 1.0 - (layer * 0.3),
        );
      }
    }
  }
}