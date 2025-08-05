import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:linch_mind/providers/app_providers.dart';
import 'package:linch_mind/services/connector_lifecycle_api_client.dart';
import 'package:linch_mind/models/connector_lifecycle_models.dart';

// Generate mocks
@GenerateMocks([ConnectorLifecycleApiClient])
import 'app_providers_test_fixed.mocks.dart';

void main() {
  group('AppState Business Logic Tests', () {
    test('should create AppState with required business rules', () {
      // Given: Business-critical app state
      final now = DateTime.now();
      final appState = AppState(
        isConnected: true,
        errorMessage: null,
        lastUpdate: now,
      );

      // Then: Should enforce business rules
      expect(appState.isConnected, true);
      expect(appState.errorMessage, null);
      expect(appState.lastUpdate, now);
      expect(appState.hasError, false); // Business logic: no error when null
    });

    test('should correctly identify error states for UI logic', () {
      // Given: App states with different error conditions
      final stateWithError = AppState(
        isConnected: false,
        errorMessage: 'Network connection failed',
        lastUpdate: DateTime.now(),
      );

      final stateWithoutError = AppState(
        isConnected: true,
        errorMessage: null,
        lastUpdate: DateTime.now(),
      );

      // Then: Should correctly identify error states for UI rendering
      expect(stateWithError.hasError, true);
      expect(stateWithoutError.hasError, false);
    });

    test('should implement immutable updates correctly', () {
      // Given: Original app state
      final original = AppState(
        isConnected: false,
        errorMessage: 'Original error',
        lastUpdate: DateTime.parse('2024-01-01T00:00:00.000Z'),
      );

      // When: Creating updated state
      final updated = original.copyWith(
        isConnected: true,
        lastUpdate: DateTime.parse('2024-01-02T00:00:00.000Z'),
      );

      // Then: Original should be unchanged (immutability)
      expect(original.isConnected, false);
      expect(original.errorMessage, 'Original error');

      // And: Updated should have new values but inherit unchanged fields
      expect(updated.isConnected, true);
      expect(updated.errorMessage, 'Original error'); // Inherited
      expect(updated.lastUpdate, DateTime.parse('2024-01-02T00:00:00.000Z'));
    });
  });

  group('AppStateNotifier State Management Tests', () {
    late ProviderContainer container;
    late AppStateNotifier notifier;

    setUp(() {
      container = ProviderContainer();
      notifier = container.read(appStateProvider.notifier);
    });

    tearDown(() {
      container.dispose();
    });

    test('should initialize with correct business defaults', () {
      // Given: Fresh notifier
      final state = container.read(appStateProvider);

      // Then: Should start in disconnected state (business requirement)
      expect(state.isConnected, false);
      expect(state.errorMessage, null);
      expect(state.lastUpdate, isA<DateTime>());
      expect(state.hasError, false);
    });

    test('should handle connection state changes with proper error clearing',
        () {
      // Given: Initial disconnected state
      var state = container.read(appStateProvider);
      expect(state.isConnected, false);

      // When: Successfully connecting
      notifier.setConnected(true);
      state = container.read(appStateProvider);

      // Then: Should clear any previous errors and set connected
      expect(state.isConnected, true);
      expect(state.errorMessage, null);
    });

    test('should set error message when connection fails', () {
      // Given: Connected state
      notifier.setConnected(true);

      // When: Connection fails
      notifier.setConnected(false);
      final state = container.read(appStateProvider);

      // Then: Should set disconnected with error message
      expect(state.isConnected, false);
      expect(state.errorMessage, 'Connection lost');
    });

    test('should handle explicit error scenarios', () {
      // Given: Normal state
      const errorMessage = 'API authentication failed';

      // When: Setting explicit error
      notifier.setError(errorMessage);
      final state = container.read(appStateProvider);

      // Then: Should set error state properly
      expect(state.isConnected, false);
      expect(state.errorMessage, errorMessage);
      expect(state.hasError, true);
    });

    test('should clear errors correctly - FIXED', () {
      // Given: State with an error
      const errorMessage = 'Test error for clearing';
      notifier.setError(errorMessage);

      var state = container.read(appStateProvider);
      expect(state.errorMessage, errorMessage);
      expect(state.hasError, true);

      // When: Clearing the error
      notifier.clearError();

      // Then: Error should be completely cleared
      state = container.read(appStateProvider);
      expect(state.errorMessage, null);
      expect(state.hasError, false);
    });

    test('should update timestamps on all state changes', () async {
      // Given: Initial state
      final initialState = container.read(appStateProvider);
      final initialTime = initialState.lastUpdate;

      // Wait to ensure timestamp difference
      await Future.delayed(const Duration(milliseconds: 10));

      // When: Making any state change
      notifier.setConnected(true);

      // Then: Timestamp should be updated
      final updatedState = container.read(appStateProvider);
      expect(updatedState.lastUpdate.isAfter(initialTime), true);
    });

    test('should handle rapid state changes gracefully', () async {
      // Given: Initial state
      final initialTime = DateTime.now();

      // When: Making rapid state changes
      notifier.setConnected(true);
      notifier.setError('Error 1');
      notifier.clearError();
      notifier.setConnected(false);
      notifier.setError('Error 2');

      // Then: Should end in consistent final state
      final finalState = container.read(appStateProvider);
      expect(finalState.isConnected, false);
      expect(finalState.errorMessage, 'Error 2');
      expect(finalState.lastUpdate.isAfter(initialTime), true);
    });
  });

  group('Provider Integration Tests', () {
    late MockConnectorLifecycleApiClient mockApiClient;
    late ProviderContainer container;

    setUp(() {
      mockApiClient = MockConnectorLifecycleApiClient();
      container = ProviderContainer(
        overrides: [
          connectorLifecycleApiProvider.overrideWithValue(mockApiClient),
        ],
      );
    });

    tearDown(() {
      container.dispose();
    });

    test('should provide correct API client instance', () {
      // Given: Container with overridden provider
      final apiClient = container.read(connectorLifecycleApiProvider);

      // Then: Should return the mocked instance
      expect(apiClient, equals(mockApiClient));
    });

    test('should handle health check provider correctly', () async {
      // Given: Mock API with health check response
      when(mockApiClient.getConnectors()).thenAnswer(
        (_) async => ConnectorListResponse(success: true, collectors: []),
      );

      // When: Reading health check provider
      final healthCheck = await container.read(healthCheckProvider.future);

      // Then: Should return correct health status
      expect(healthCheck, true);
      verify(mockApiClient.getConnectors()).called(1);
    });

    test('should handle health check failures', () async {
      // Given: Mock API that throws exception
      when(mockApiClient.getConnectors()).thenThrow(
        Exception('Health check failed'),
      );

      // When: Reading health check provider
      final healthCheck = await container.read(healthCheckProvider.future);

      // Then: Should return false for failed health check
      expect(healthCheck, false);
      verify(mockApiClient.getConnectors()).called(1);
    });

    test('should handle connector definitions provider', () async {
      // Given: Mock API with connector definitions
      final mockDefinitions = [
        ConnectorDefinition(
          connectorId: 'test-connector',
          name: 'Test Connector',
          displayName: 'Test Connector Display',
          description: 'Test connector description',
          category: 'test',
          version: '1.0.0',
          author: 'Test Author',
        ),
      ];

      when(mockApiClient.discoverConnectors()).thenAnswer(
        (_) async => DiscoveryResponse(
            success: true, message: 'Success', connectors: mockDefinitions),
      );

      // When: Reading connector definitions
      final definitions =
          await container.read(connectorDefinitionsProvider.future);

      // Then: Should return correct definitions
      expect(definitions, equals(mockDefinitions));
      verify(mockApiClient.discoverConnectors()).called(1);
    });

    test('should handle connectors provider', () async {
      // Given: Mock API with connectors
      final mockConnectors = [
        ConnectorInfo(
          collectorId: 'test-collector',
          displayName: 'Test Collector',
          state: ConnectorState.running,
          enabled: true,
          config: const {},
        ),
      ];

      when(mockApiClient.getConnectors()).thenAnswer(
        (_) async =>
            ConnectorListResponse(success: true, collectors: mockConnectors),
      );

      // When: Reading connectors
      final connectors = await container.read(connectorsProvider.future);

      // Then: Should return correct connectors
      expect(connectors, equals(mockConnectors));
      verify(mockApiClient.getConnectors()).called(1);
    });
  });

  group('ConnectorInstanceStateNotifier Tests', () {
    late MockConnectorLifecycleApiClient mockApiClient;
    late ProviderContainer container;
    const testInstanceId = 'test-instance-123';

    setUp(() {
      mockApiClient = MockConnectorLifecycleApiClient();
      container = ProviderContainer(
        overrides: [
          connectorLifecycleApiProvider.overrideWithValue(mockApiClient),
        ],
      );
    });

    tearDown(() {
      container.dispose();
    });

    test('should initialize with correct default state', () {
      // Given: Fresh connector instance notifier
      final state =
          container.read(connectorInstanceStateProvider(testInstanceId));

      // Then: Should have correct initial state
      expect(state.instanceId, testInstanceId);
      expect(state.state, ConnectorState.configured);
      expect(state.isLoading, false);
      expect(state.errorMessage, null);
    });

    test('should handle start connector operation', () async {
      // Given: Stopped connector instance
      when(mockApiClient.startConnector(testInstanceId)).thenAnswer((_) async {
        await Future.delayed(const Duration(milliseconds: 50));
        return OperationResponse(
            success: true,
            message: 'Started',
            instanceId: testInstanceId,
            state: ConnectorState.running);
      });

      // When: Starting the connector
      final notifier = container
          .read(connectorInstanceStateProvider(testInstanceId).notifier);

      // Should show loading state initially
      final startFuture = notifier.startInstance();
      await Future.delayed(const Duration(milliseconds: 1));

      var state =
          container.read(connectorInstanceStateProvider(testInstanceId));
      expect(state.isLoading, true);
      expect(state.errorMessage, null);

      // Complete the operation
      await startFuture;

      // Then: Should be in running state
      state = container.read(connectorInstanceStateProvider(testInstanceId));
      expect(state.state, ConnectorState.running);
      expect(state.isLoading, false);
      expect(state.errorMessage, null);

      verify(mockApiClient.startConnector(testInstanceId)).called(1);
    });

    test('should handle start connector failure', () async {
      // Given: API that fails to start connector
      const errorMessage = 'Failed to start connector';
      when(mockApiClient.startConnector(testInstanceId))
          .thenThrow(Exception(errorMessage));

      // When: Attempting to start connector
      final notifier = container
          .read(connectorInstanceStateProvider(testInstanceId).notifier);
      await notifier.startInstance();

      // Then: Should be in error state
      final state =
          container.read(connectorInstanceStateProvider(testInstanceId));
      expect(state.state, ConnectorState.error);
      expect(state.isLoading, false);
      expect(state.errorMessage, contains(errorMessage));
    });

    test('should handle stop connector operation', () async {
      // Given: Running connector instance
      when(mockApiClient.stopConnector(testInstanceId)).thenAnswer((_) async =>
          OperationResponse(
              success: true,
              message: 'Stopped',
              instanceId: testInstanceId,
              state: ConnectorState.enabled));

      // When: Stopping the connector
      final notifier = container
          .read(connectorInstanceStateProvider(testInstanceId).notifier);
      await notifier.stopInstance();

      // Then: Should be in enabled state
      final state =
          container.read(connectorInstanceStateProvider(testInstanceId));
      expect(state.state, ConnectorState.enabled);
      expect(state.isLoading, false);
      expect(state.errorMessage, null);

      verify(mockApiClient.stopConnector(testInstanceId)).called(1);
    });

    test('should handle restart connector operation', () async {
      // Given: Running connector that needs restart
      when(mockApiClient.restartConnector(testInstanceId)).thenAnswer(
          (_) async => OperationResponse(
              success: true,
              message: 'Restarted',
              instanceId: testInstanceId,
              state: ConnectorState.running));

      // When: Restarting the connector
      final notifier = container
          .read(connectorInstanceStateProvider(testInstanceId).notifier);
      await notifier.restartInstance();

      // Then: Should be back in running state
      final state =
          container.read(connectorInstanceStateProvider(testInstanceId));
      expect(state.state, ConnectorState.running);
      expect(state.isLoading, false);
      expect(state.errorMessage, null);
    });
  });
}

// Import the actual response models - no need for custom mock classes
