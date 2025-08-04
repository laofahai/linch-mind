import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:linch_mind/providers/app_providers.dart';

void main() {
  group('AppState', () {
    test('should create AppState with all fields', () {
      final appState = AppState(
        isConnected: true,
        errorMessage: null,
        lastUpdate: DateTime.now(),
      );

      expect(appState.isConnected, true);
      expect(appState.errorMessage, null);
      expect(appState.lastUpdate, isA<DateTime>());
    });

    test('should create copy with copyWith method', () {
      final now = DateTime.now();
      final appState = AppState(
        isConnected: false,
        errorMessage: 'Test error',
        lastUpdate: now,
      );

      final updatedState = appState.copyWith(
        isConnected: true,
      );

      expect(updatedState.isConnected, true);
      expect(updatedState.errorMessage, 'Test error'); // Should remain the same since we didn't override it
      expect(updatedState.lastUpdate, now); // Should remain the same
    });
  });

  group('AppStateNotifier', () {
    late ProviderContainer container;
    late AppStateNotifier notifier;

    setUp(() {
      container = ProviderContainer();
      notifier = container.read(appStateProvider.notifier);
    });

    tearDown(() {
      container.dispose();
    });

    test('should initialize with disconnected state', () {
      final state = container.read(appStateProvider);
      
      expect(state.isConnected, false);
      expect(state.errorMessage, null);
      expect(state.lastUpdate, isA<DateTime>());
    });

    test('should set connected state', () {
      notifier.setConnected(true);
      
      final state = container.read(appStateProvider);
      expect(state.isConnected, true);
      expect(state.errorMessage, null);
    });

    test('should set disconnected state with error message', () {
      notifier.setConnected(false);
      
      final state = container.read(appStateProvider);
      expect(state.isConnected, false);
      expect(state.errorMessage, 'Connection lost');
    });

    test('should set error message', () {
      const errorMessage = 'Network error occurred';
      notifier.setError(errorMessage);
      
      final state = container.read(appStateProvider);
      expect(state.isConnected, false);
      expect(state.errorMessage, errorMessage);
    });

    test('should clear error message', () {
      // First set an error
      notifier.setError('Test error');
      var currentState = container.read(appStateProvider);
      expect(currentState.errorMessage, 'Test error');
      
      // Then clear it
      notifier.clearError();
      currentState = container.read(appStateProvider);
      expect(currentState.errorMessage, null);
    });

    test('should update lastUpdate timestamp on state changes', () async {
      final initialState = container.read(appStateProvider);
      final initialTime = initialState.lastUpdate;
      
      // Wait a small amount to ensure timestamp difference
      await Future.delayed(const Duration(milliseconds: 10));
      
      notifier.setConnected(true);
      
      final updatedState = container.read(appStateProvider);
      expect(updatedState.lastUpdate.isAfter(initialTime), true);
    });
  });

  group('Provider dependencies', () {
    test('should provide correct instances', () {
      final container = ProviderContainer();
      
      // Test that providers can be read without throwing
      expect(() => container.read(appStateProvider), returnsNormally);
      expect(() => container.read(connectorLifecycleApiProvider), returnsNormally);
      
      container.dispose();
    });

    test('should handle provider overrides', () {
      // This test would be more meaningful with actual mock implementations
      // For now, we just verify the structure
      final container = ProviderContainer();
      
      final appState = container.read(appStateProvider);
      expect(appState, isA<AppState>());
      
      container.dispose();
    });
  });
}