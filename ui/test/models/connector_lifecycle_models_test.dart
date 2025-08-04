import 'package:flutter_test/flutter_test.dart';
import 'package:linch_mind/models/connector_lifecycle_models.dart';

void main() {
  group('ConnectorDefinition', () {
    test('should create ConnectorDefinition with required fields', () {
      final connector = ConnectorDefinition(
        connectorId: 'test-connector',
        name: 'filesystem',
        displayName: 'File System Connector',
        description: 'Test connector for filesystem',
        category: 'data',
        version: '1.0.0',
        author: 'test-author',
      );

      expect(connector.connectorId, 'test-connector');
      expect(connector.name, 'filesystem');
      expect(connector.displayName, 'File System Connector');
      expect(connector.description, 'Test connector for filesystem');
      expect(connector.category, 'data');
      expect(connector.version, '1.0.0');
      expect(connector.author, 'test-author');
    });

    test('should have default values for optional fields', () {
      final connector = ConnectorDefinition(
        connectorId: 'test-connector',
        name: 'filesystem',
        displayName: 'File System Connector',
        description: 'Test connector',
        category: 'data',
        version: '1.0.0',
        author: 'test-author',
      );

      expect(connector.license, '');
      expect(connector.autoDiscovery, false);
      expect(connector.hotConfigReload, true);
      expect(connector.healthCheck, true);
      expect(connector.entryPoint, 'main.py');
      expect(connector.dependencies, isEmpty);
      expect(connector.permissions, isEmpty);
      expect(connector.configSchema, isEmpty);
      expect(connector.defaultConfig, isEmpty);
    });
  });

  group('ConnectorState enum', () {
    test('should have all required states', () {
      expect(ConnectorState.values, contains(ConnectorState.available));
      expect(ConnectorState.values, contains(ConnectorState.installed));
      expect(ConnectorState.values, contains(ConnectorState.configured));
      expect(ConnectorState.values, contains(ConnectorState.enabled));
      expect(ConnectorState.values, contains(ConnectorState.running));
      expect(ConnectorState.values, contains(ConnectorState.error));
      expect(ConnectorState.values, contains(ConnectorState.stopping));
      expect(ConnectorState.values, contains(ConnectorState.updating));
      expect(ConnectorState.values, contains(ConnectorState.uninstalling));
    });
  });

  group('ConnectorInfo', () {
    test('should create ConnectorInfo with all fields', () {
      final connectorInfo = ConnectorInfo(
        collectorId: 'collector-1',
        displayName: 'My File System',
        state: ConnectorState.running,
        enabled: true,
        autoStart: true,
        processId: 12345,
        lastHeartbeat: DateTime.parse('2024-01-01T00:00:00.000Z'),
        dataCount: 100,
        errorMessage: null,
        createdAt: DateTime.parse('2024-01-01T00:00:00.000Z'),
        updatedAt: DateTime.parse('2024-01-01T00:00:00.000Z'),
        config: const {'path': '/test/path'},
      );

      expect(connectorInfo.collectorId, 'collector-1');
      expect(connectorInfo.displayName, 'My File System');
      expect(connectorInfo.state, ConnectorState.running);
      expect(connectorInfo.enabled, true);
      expect(connectorInfo.autoStart, true);
      expect(connectorInfo.processId, 12345);
      expect(connectorInfo.dataCount, 100);
      expect(connectorInfo.config['path'], '/test/path');
    });

    test('should create ConnectorInfo with default values', () {
      final connectorInfo = ConnectorInfo(
        collectorId: 'collector-2',
        displayName: 'Test Connector',
        state: ConnectorState.configured,
      );

      expect(connectorInfo.enabled, true);
      expect(connectorInfo.autoStart, true);
      expect(connectorInfo.dataCount, 0);
      expect(connectorInfo.config, isEmpty);
      expect(connectorInfo.processId, null);
    });
  });
}