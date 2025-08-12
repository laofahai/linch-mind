// 数据洞察状态管理
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/data_insights_models.dart';
import '../services/data_insights_service.dart';
import '../services/ipc_client.dart';
import '../utils/app_logger.dart';

// IPC客户端提供者
final ipcClientProvider = Provider<IPCClient>((ref) {
  return IPCClient();
});

// 服务提供者
final dataInsightsServiceProvider = Provider<DataInsightsService>((ref) {
  final ipcClient = ref.read(ipcClientProvider);
  return DataInsightsService(ipcClient);
});

// 数据洞察概览状态
class DataInsightsState {
  final DataInsightsOverview? overview;
  final bool isLoading;
  final String? error;
  final DateTime? lastRefresh;

  const DataInsightsState({
    this.overview,
    this.isLoading = false,
    this.error,
    this.lastRefresh,
  });

  DataInsightsState copyWith({
    DataInsightsOverview? overview,
    bool? isLoading,
    String? error,
    DateTime? lastRefresh,
  }) {
    return DataInsightsState(
      overview: overview ?? this.overview,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      lastRefresh: lastRefresh ?? this.lastRefresh,
    );
  }
}

// 数据洞察状态通知器
class DataInsightsNotifier extends StateNotifier<DataInsightsState> {
  final DataInsightsService _service;

  DataInsightsNotifier(this._service) : super(const DataInsightsState()) {
    _initialize();
  }

  void _initialize() {
    // 监听服务的数据流
    _service.overviewStream.listen((overview) {
      state = state.copyWith(
        overview: overview,
        lastRefresh: DateTime.now(),
        error: null,
      );
    });

    // 初始加载
    refresh();
  }

  /// 刷新数据
  Future<void> refresh() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      AppLogger.info('刷新数据洞察', module: 'DataInsightsProvider');
      final overview = await _service.getOverview();
      
      state = state.copyWith(
        overview: overview,
        isLoading: false,
        lastRefresh: DateTime.now(),
        error: null,
      );
    } catch (e) {
      AppLogger.error('刷新数据洞察失败: $e', module: 'DataInsightsProvider');
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// 重置错误状态
  void clearError() {
    state = state.copyWith(error: null);
  }
}

// 数据洞察状态提供者
final dataInsightsProvider =
    StateNotifierProvider<DataInsightsNotifier, DataInsightsState>((ref) {
  final service = ref.read(dataInsightsServiceProvider);
  return DataInsightsNotifier(service);
});

// 实体列表状态
class EntityListState {
  final List<EntityDetail> entities;
  final bool isLoading;
  final String? error;
  final bool hasMore;
  final String? currentType;
  final String? searchQuery;

  const EntityListState({
    this.entities = const [],
    this.isLoading = false,
    this.error,
    this.hasMore = true,
    this.currentType,
    this.searchQuery,
  });

  EntityListState copyWith({
    List<EntityDetail>? entities,
    bool? isLoading,
    String? error,
    bool? hasMore,
    String? currentType,
    String? searchQuery,
  }) {
    return EntityListState(
      entities: entities ?? this.entities,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      hasMore: hasMore ?? this.hasMore,
      currentType: currentType ?? this.currentType,
      searchQuery: searchQuery ?? this.searchQuery,
    );
  }
}

// 实体列表状态通知器
class EntityListNotifier extends StateNotifier<EntityListState> {
  final DataInsightsService _service;

  EntityListNotifier(this._service) : super(const EntityListState());

  /// 加载实体列表
  Future<void> loadEntities({String? type, bool refresh = false}) async {
    if (refresh) {
      state = const EntityListState(isLoading: true);
    } else {
      state = state.copyWith(isLoading: true, error: null);
    }

    try {
      final entities = await _service.getEntities(type: type);
      
      state = state.copyWith(
        entities: entities,
        isLoading: false,
        currentType: type,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// 搜索实体
  Future<void> searchEntities(String query) async {
    state = state.copyWith(isLoading: true, error: null, searchQuery: query);

    try {
      final entities = await _service.searchEntities(query);
      
      state = state.copyWith(
        entities: entities,
        isLoading: false,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// 清除搜索
  void clearSearch() {
    state = state.copyWith(searchQuery: null);
    loadEntities(type: state.currentType, refresh: true);
  }
}

// 实体列表提供者
final entityListProvider =
    StateNotifierProvider<EntityListNotifier, EntityListState>((ref) {
  final service = ref.read(dataInsightsServiceProvider);
  return EntityListNotifier(service);
});

// 时间线状态
class TimelineState {
  final List<TimelineItem> items;
  final bool isLoading;
  final String? error;

  const TimelineState({
    this.items = const [],
    this.isLoading = false,
    this.error,
  });

  TimelineState copyWith({
    List<TimelineItem>? items,
    bool? isLoading,
    String? error,
  }) {
    return TimelineState(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

// 时间线状态通知器
class TimelineNotifier extends StateNotifier<TimelineState> {
  final DataInsightsService _service;

  TimelineNotifier(this._service) : super(const TimelineState()) {
    _initialize();
  }

  void _initialize() {
    // 监听时间线数据流
    _service.timelineStream.listen((items) {
      state = state.copyWith(items: items, error: null);
    });

    // 初始加载
    loadTimeline();
  }

  /// 加载时间线
  Future<void> loadTimeline() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final items = await _service.getTimeline();
      
      state = state.copyWith(
        items: items,
        isLoading: false,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }
}

// 时间线提供者
final timelineProvider =
    StateNotifierProvider<TimelineNotifier, TimelineState>((ref) {
  final service = ref.read(dataInsightsServiceProvider);
  return TimelineNotifier(service);
});

// 筛选选项状态
final filterOptionsProvider = StateProvider<FilterOptions>((ref) {
  return const FilterOptions();
});

// 当前选中的实体类型
final selectedEntityTypeProvider = StateProvider<String?>((ref) => null);

// 搜索查询
final searchQueryProvider = StateProvider<String>((ref) => '');

// 是否显示详细视图
final showDetailViewProvider = StateProvider<bool>((ref) => false);