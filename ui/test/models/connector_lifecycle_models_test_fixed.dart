import 'package:flutter_test/flutter_test.dart';
import 'package:linch_mind/models/connector_lifecycle_models.dart';

void main() {
  group('ConnectorDefinition Business Logic Tests', () {
    test('should enforce required business fields correctly', () {
      // Given: Valid connector definition data
      final connector = ConnectorDefinition(
        connectorId: 'filesystem-v2',
        name: 'filesystem',
        displayName: 'Advanced File System Connector',
        description: 'Monitors file system changes with advanced filtering',
        category: 'data-collection',
        version: '2.1.0',
        author: 'Linch Mind Team',
        license: 'MIT',
        autoDiscovery: true,
        hotConfigReload: true,
        healthCheck: true,
        entryPoint: 'filesystem_connector.py',
        dependencies: ['watchdog>=2.0.0', 'pathlib2>=2.3.0'],
        permissions: ['file.read', 'file.watch'],
        configSchema: {
          'type': 'object',
          'properties': {
            'watchPath': {'type': 'string', 'required': true},
            'recursive': {'type': 'boolean', 'default': true},
            'fileTypes': {
              'type': 'array',
              'items': {'type': 'string'}
            },
          }
        },
        defaultConfig: {
          'watchPath': '/home/user/Documents',
          'recursive': true,
          'fileTypes': ['.txt', '.md', '.pdf'],
        },
      );

      // Then: All business-critical fields should be properly set
      expect(connector.connectorId, 'filesystem-v2');
      expect(connector.name, 'filesystem');
      expect(connector.displayName, 'Advanced File System Connector');
      expect(connector.category, 'data-collection');
      expect(connector.version, '2.1.0');
      expect(connector.author, 'Linch Mind Team');

      // And: Should have proper default behaviors for operations
      expect(connector.autoDiscovery, true);
      expect(connector.hotConfigReload, true);
      expect(connector.healthCheck, true);

      // And: Should have valid configuration structure
      expect(connector.configSchema, isNotEmpty);
      expect(connector.defaultConfig, isNotEmpty);
      expect(connector.dependencies, isNotEmpty);
      expect(connector.permissions, isNotEmpty);
    });

    test('should apply correct defaults for optional fields', () {
      // Given: Minimal connector definition (business minimum requirements)
      final connector = ConnectorDefinition(
        connectorId: 'minimal-connector',
        name: 'minimal',
        displayName: 'Minimal Test Connector',
        description: 'Basic connector for testing',
        category: 'test',
        version: '1.0.0',
        author: 'Test Suite',
      );

      // Then: Should apply business-appropriate defaults
      expect(connector.license, ''); // No license by default
      expect(connector.autoDiscovery, false); // Conservative default
      expect(connector.hotConfigReload, true); // User-friendly default
      expect(connector.healthCheck, true); // Reliability default
      expect(connector.entryPoint, 'main.py'); // Convention default
      expect(connector.dependencies, isEmpty); // No deps by default
      expect(connector.permissions, isEmpty); // Secure by default
      expect(connector.configSchema, isEmpty); // No schema requirements
      expect(connector.defaultConfig, isEmpty); // No default config
    });

    test('should validate version format for business compliance', () {
      // Given: Various version formats
      final validVersions = ['1.0.0', '2.1.3', '0.9.0-beta', '1.0.0-alpha.1'];
      final invalidVersions = ['1.0', 'v1.0.0', 'latest', ''];

      for (final version in validVersions) {
        // When: Creating connector with valid version
        final connector = ConnectorDefinition(
          connectorId: 'version-test',
          name: 'test',
          displayName: 'Version Test',
          description: 'Testing version validation',
          category: 'test',
          version: version,
          author: 'Test',
        );

        // Then: Should accept valid semantic versions
        expect(connector.version, version);
        expect(_isValidSemanticVersion(version), true);
      }

      // Invalid versions should be caught by business logic
      for (final version in invalidVersions) {
        expect(_isValidSemanticVersion(version), false);
      }
    });

    test('should handle complex configuration schemas correctly', () {
      // Given: Connector with complex configuration requirements
      final complexSchema = {
        'type': 'object',
        'properties': {
          'database': {
            'type': 'object',
            'properties': {
              'host': {'type': 'string', 'required': true},
              'port': {'type': 'integer', 'minimum': 1, 'maximum': 65535},
              'ssl': {'type': 'boolean', 'default': true},
            },
            'required': ['host']
          },
          'filters': {
            'type': 'array',
            'items': {
              'type': 'object',
              'properties': {
                'pattern': {'type': 'string'},
                'action': {
                  'type': 'string',
                  'enum': ['include', 'exclude']
                },
              }
            }
          },
          'advanced': {
            'type': 'object',
            'properties': {
              'batchSize': {'type': 'integer', 'default': 1000},
              'timeout': {'type': 'integer', 'default': 30000},
            }
          }
        },
        'required': ['database']
      };

      final connector = ConnectorDefinition(
        connectorId: 'complex-db-connector',
        name: 'database',
        displayName: 'Database Connector',
        description: 'Complex database integration connector',
        category: 'database',
        version: '1.0.0',
        author: 'DB Team',
        configSchema: complexSchema,
      );

      // Then: Should preserve complex schema structure
      expect(connector.configSchema, equals(complexSchema));
      expect(connector.configSchema['properties'], isA<Map>());
      expect(connector.configSchema['properties']['database'], isA<Map>());
      expect(connector.configSchema['required'], contains('database'));
    });
  });

  group('ConnectorState Business Logic Tests', () {
    test('should represent all valid connector lifecycle states', () {
      // Given: All possible connector states
      const allStates = [
        ConnectorState.available,
        ConnectorState.installed,
        ConnectorState.configured,
        ConnectorState.enabled,
        ConnectorState.running,
        ConnectorState.error,
        ConnectorState.stopping,
        ConnectorState.updating,
        ConnectorState.uninstalling,
      ];

      // Then: Each state should have proper business meaning
      for (final state in allStates) {
        expect(state.toString(), contains('ConnectorState.'));
        expect(state.name, isNotEmpty);
      }

      // And: Should cover all business lifecycle stages
      expect(allStates, hasLength(9)); // Ensure we account for all states
    });

    test('should validate state transition business rules', () {
      // Given: Business rules for state transitions
      final validTransitions = {
        ConnectorState.available: [ConnectorState.installed],
        ConnectorState.installed: [
          ConnectorState.configured,
          ConnectorState.uninstalling
        ],
        ConnectorState.configured: [
          ConnectorState.enabled,
          ConnectorState.uninstalling
        ],
        ConnectorState.enabled: [
          ConnectorState.running,
          ConnectorState.configured
        ],
        ConnectorState.running: [ConnectorState.stopping, ConnectorState.error],
        ConnectorState.stopping: [ConnectorState.enabled, ConnectorState.error],
        ConnectorState.error: [
          ConnectorState.configured,
          ConnectorState.enabled,
          ConnectorState.uninstalling
        ],
        ConnectorState.updating: [
          ConnectorState.configured,
          ConnectorState.error
        ],
        ConnectorState.uninstalling: [
          ConnectorState.available,
          ConnectorState.error
        ],
      };

      // Then: Each state should have logical next states
      for (final entry in validTransitions.entries) {
        final currentState = entry.key;
        final nextStates = entry.value;

        expect(nextStates, isNotEmpty,
            reason: 'State $currentState should have valid next states');

        // Verify business logic makes sense for each transition
        if (currentState != ConnectorState.uninstalling) {
          // Only uninstalling can go back to available
          expect(nextStates, isNot(contains(ConnectorState.available)),
              reason:
                  'Only uninstalling state should transition back to available');
        }
      }
    });

    test('should identify terminal and transitional states', () {
      // Given: Different categories of states
      const terminalStates = [ConnectorState.error];
      const activeStates = [ConnectorState.running];
      const transitionalStates = [
        ConnectorState.stopping,
        ConnectorState.updating,
        ConnectorState.uninstalling
      ];
      const configurationStates = [
        ConnectorState.available,
        ConnectorState.installed,
        ConnectorState.configured,
        ConnectorState.enabled,
      ];

      // Then: Should correctly categorize states for business logic
      for (final state in terminalStates) {
        expect(_isTerminalState(state), true);
        expect(_requiresUserAction(state), true);
      }

      for (final state in activeStates) {
        expect(_isActiveState(state), true);
        expect(_isStableState(state), true);
      }

      for (final state in transitionalStates) {
        expect(_isTransitionalState(state), true);
        expect(_isStableState(state), false);
      }

      for (final state in configurationStates) {
        expect(_isConfigurationState(state), true);
      }
    });
  });

  group('ConnectorInfo Business Logic Tests', () {
    test('should track connector runtime state correctly', () {
      // Given: Running connector with all runtime information
      final runningConnector = ConnectorInfo(
        collectorId: 'prod-filesystem-001',
        displayName: 'Production File System Monitor',
        state: ConnectorState.running,
        enabled: true,
        autoStart: true,
        processId: 12345,
        lastHeartbeat: DateTime.parse('2024-01-15T10:30:00.000Z'),
        dataCount: 15420,
        errorMessage: null,
        createdAt: DateTime.parse('2024-01-01T08:00:00.000Z'),
        updatedAt: DateTime.parse('2024-01-15T10:30:00.000Z'),
        config: const {
          'watchPath': '/data/important',
          'recursive': true,
          'fileTypes': ['.log', '.txt', '.json'],
          'batchSize': 100,
        },
      );

      // Then: Should accurately reflect runtime state
      expect(runningConnector.collectorId, 'prod-filesystem-001');
      expect(runningConnector.state, ConnectorState.running);
      expect(runningConnector.enabled, true);
      expect(runningConnector.autoStart, true);
      expect(runningConnector.processId, 12345);
      expect(runningConnector.dataCount, 15420);
      expect(runningConnector.errorMessage, null);

      // And: Should have proper configuration
      expect(runningConnector.config['watchPath'], '/data/important');
      expect(runningConnector.config['recursive'], true);
      expect(runningConnector.config['batchSize'], 100);
    });

    test('should handle error states with diagnostic information', () {
      // Given: Connector in error state
      const errorMessage =
          'Permission denied: Cannot access /protected/directory';
      final errorConnector = ConnectorInfo(
        collectorId: 'failed-filesystem-002',
        displayName: 'Failed File System Monitor',
        state: ConnectorState.error,
        enabled: true,
        autoStart: false, // Disabled auto-start due to persistent errors
        processId: null, // No process when in error
        lastHeartbeat: DateTime.parse('2024-01-15T09:45:00.000Z'),
        dataCount: 0, // No data processed due to error
        errorMessage: errorMessage,
        createdAt: DateTime.parse('2024-01-15T09:00:00.000Z'),
        updatedAt: DateTime.parse('2024-01-15T09:45:00.000Z'),
        config: const {
          'watchPath': '/protected/directory',
          'recursive': true,
        },
      );

      // Then: Should properly represent error state
      expect(errorConnector.state, ConnectorState.error);
      expect(errorConnector.processId, null);
      expect(errorConnector.dataCount, 0);
      expect(errorConnector.errorMessage, errorMessage);
      expect(errorConnector.autoStart, false);

      // And: Should preserve problematic configuration for diagnosis
      expect(errorConnector.config['watchPath'], '/protected/directory');
    });

    test('should handle stopped connectors with proper defaults', () {
      // Given: Minimal stopped connector
      final stoppedConnector = ConnectorInfo(
        collectorId: 'stopped-test-connector',
        displayName: 'Stopped Test Connector',
        state: ConnectorState.enabled, // Enabled but not running
      );

      // Then: Should have appropriate defaults for stopped state
      expect(stoppedConnector.state, ConnectorState.enabled);
      expect(stoppedConnector.enabled, true); // Default enabled
      expect(stoppedConnector.autoStart, true); // Default auto-start
      expect(stoppedConnector.processId, null); // No process when stopped
      expect(stoppedConnector.dataCount, 0); // Default data count
      expect(stoppedConnector.errorMessage, null); // No error by default
      expect(stoppedConnector.config, isEmpty); // Empty config by default
    });

    test('should validate business rules for connector state consistency', () {
      // Given: Different connector configurations
      final testCases = [
        // Running connector must have process ID
        (state: ConnectorState.running, processId: 1234, shouldBeValid: true),
        (state: ConnectorState.running, processId: null, shouldBeValid: false),

        // Stopped connector should not have process ID
        (state: ConnectorState.enabled, processId: null, shouldBeValid: true),
        (state: ConnectorState.enabled, processId: 1234, shouldBeValid: false),

        // Error state should not have process ID
        (state: ConnectorState.error, processId: null, shouldBeValid: true),
        (state: ConnectorState.error, processId: 1234, shouldBeValid: false),
      ];

      for (final testCase in testCases) {
        final connector = ConnectorInfo(
          collectorId: 'validation-test',
          displayName: 'Validation Test',
          state: testCase.state,
          processId: testCase.processId,
        );

        final isValid = _validateConnectorState(connector);
        expect(isValid, testCase.shouldBeValid,
            reason:
                'State ${testCase.state} with processId ${testCase.processId} '
                'should be ${testCase.shouldBeValid ? "valid" : "invalid"}');
      }
    });
  });

  group('Serialization Business Logic Tests', () {
    test('should serialize connector definition with all business data', () {
      // Given: Complete connector definition
      final connector = ConnectorDefinition(
        connectorId: 'production-database-v3',
        name: 'database',
        displayName: 'Production Database Connector v3',
        description:
            'High-performance database integration with advanced features',
        category: 'database',
        version: '3.2.1',
        author: 'Database Team <db-team@linch-mind.com>',
        license: 'Commercial',
        autoDiscovery: true,
        hotConfigReload: false, // Disabled for production safety
        healthCheck: true,
        entryPoint: 'db_connector_v3.py',
        dependencies: [
          'sqlalchemy>=1.4.0',
          'psycopg2-binary>=2.9.0',
          'redis>=4.0.0',
        ],
        permissions: [
          'database.read',
          'database.write',
          'cache.read',
          'cache.write',
        ],
        configSchema: {
          'type': 'object',
          'properties': {
            'database_url': {'type': 'string', 'format': 'uri'},
            'pool_size': {'type': 'integer', 'minimum': 1, 'maximum': 100},
            'ssl_mode': {
              'type': 'string',
              'enum': ['disable', 'require', 'verify-full']
            },
          },
          'required': ['database_url'],
        },
        defaultConfig: {
          'database_url': 'postgresql://localhost:5432/linch_mind',
          'pool_size': 20,
          'ssl_mode': 'require',
        },
      );

      // When: Serializing to JSON
      final json = connector.toJson();

      // Then: Should preserve all business-critical information
      expect(json['connector_id'], 'production-database-v3');
      expect(json['name'], 'database');
      expect(json['display_name'], 'Production Database Connector v3');
      expect(json['category'], 'database');
      expect(json['version'], '3.2.1');
      expect(json['author'], 'Database Team <db-team@linch-mind.com>');
      expect(json['license'], 'Commercial');

      // And: Should preserve operational settings
      expect(json['auto_discovery'], true);
      expect(json['hot_config_reload'], false);
      expect(json['health_check'], true);
      expect(json['entry_point'], 'db_connector_v3.py');

      // And: Should preserve dependencies and permissions
      expect(json['dependencies'], isA<List>());
      expect(json['dependencies'], contains('sqlalchemy>=1.4.0'));
      expect(json['permissions'], contains('database.read'));

      // And: Should preserve complex configuration schema
      expect(json['config_schema'], isA<Map>());
      expect(json['config_schema']['properties'], isA<Map>());
      expect(json['default_config'], isA<Map>());
      expect(json['default_config']['database_url'], isA<String>());
    });

    test('should deserialize connector definition maintaining data integrity',
        () {
      // Given: Complete JSON representation
      final jsonData = {
        'connector_id': 'filesystem-advanced-v2',
        'name': 'filesystem-advanced',
        'display_name': 'Advanced File System Monitor v2',
        'description':
            'Advanced file system monitoring with ML-based pattern detection',
        'category': 'file-monitoring',
        'version': '2.0.0-beta.3',
        'author': 'AI Team',
        'license': 'Apache-2.0',
        'auto_discovery': true,
        'hot_config_reload': true,
        'health_check': true,
        'entry_point': 'advanced_fs_monitor.py',
        'dependencies': [
          'watchdog>=2.1.0',
          'scikit-learn>=1.0.0',
          'numpy>=1.21.0',
        ],
        'permissions': [
          'file.read',
          'file.watch',
          'ml.predict',
        ],
        'config_schema': {
          'type': 'object',
          'properties': {
            'watch_paths': {
              'type': 'array',
              'items': {'type': 'string'},
              'minItems': 1,
            },
            'ml_model_path': {
              'type': 'string',
              'default': 'models/file_classifier.pkl',
            },
            'sensitivity': {
              'type': 'number',
              'minimum': 0.0,
              'maximum': 1.0,
              'default': 0.7,
            },
          },
          'required': ['watch_paths'],
        },
        'default_config': {
          'watch_paths': ['/home/user/Documents', '/home/user/Projects'],
          'ml_model_path': 'models/file_classifier.pkl',
          'sensitivity': 0.7,
        },
      };

      // When: Deserializing from JSON
      final connector = ConnectorDefinition.fromJson(jsonData);

      // Then: Should reconstruct all business data correctly
      expect(connector.connectorId, 'filesystem-advanced-v2');
      expect(connector.name, 'filesystem-advanced');
      expect(connector.displayName, 'Advanced File System Monitor v2');
      expect(connector.category, 'file-monitoring');
      expect(connector.version, '2.0.0-beta.3');
      expect(connector.author, 'AI Team');
      expect(connector.license, 'Apache-2.0');

      // And: Should preserve operational settings
      expect(connector.autoDiscovery, true);
      expect(connector.hotConfigReload, true);
      expect(connector.healthCheck, true);
      expect(connector.entryPoint, 'advanced_fs_monitor.py');

      // And: Should preserve complex arrays and objects
      expect(connector.dependencies, hasLength(3));
      expect(connector.dependencies, contains('scikit-learn>=1.0.0'));
      expect(connector.permissions, contains('ml.predict'));

      // And: Should preserve nested configuration structures
      expect(connector.configSchema['properties']['watch_paths'], isA<Map>());
      expect(
          connector.configSchema['properties']['sensitivity']['minimum'], 0.0);
      expect(connector.defaultConfig['watch_paths'], isA<List>());
      expect(connector.defaultConfig['sensitivity'], 0.7);
    });

    test('should handle serialization round-trip without data loss', () {
      // Given: Complex connector definition
      final original = ConnectorDefinition(
        connectorId: 'roundtrip-test-connector',
        name: 'roundtrip-test',
        displayName: 'Round Trip Test Connector',
        description: 'Testing serialization round-trip integrity',
        category: 'test',
        version: '1.0.0-alpha.1+build.123',
        author: 'Test Suite',
        license: 'MIT',
        autoDiscovery: false,
        hotConfigReload: true,
        healthCheck: false,
        entryPoint: 'test_connector.py',
        dependencies: ['pytest>=6.0.0', 'mock>=4.0.0'],
        permissions: ['test.read', 'test.write'],
        configSchema: {
          'type': 'object',
          'properties': {
            'nested': {
              'type': 'object',
              'properties': {
                'deep': {'type': 'string', 'default': 'value'},
              },
            },
          },
        },
        defaultConfig: {
          'nested': {'deep': 'value'},
          'array': [1, 2, 3],
          'boolean': true,
          'null_value': null,
        },
      );

      // When: Performing round-trip serialization
      final json = original.toJson();
      final deserialized = ConnectorDefinition.fromJson(json);

      // Then: Should be identical to original
      expect(deserialized.connectorId, original.connectorId);
      expect(deserialized.name, original.name);
      expect(deserialized.displayName, original.displayName);
      expect(deserialized.description, original.description);
      expect(deserialized.category, original.category);
      expect(deserialized.version, original.version);
      expect(deserialized.author, original.author);
      expect(deserialized.license, original.license);
      expect(deserialized.autoDiscovery, original.autoDiscovery);
      expect(deserialized.hotConfigReload, original.hotConfigReload);
      expect(deserialized.healthCheck, original.healthCheck);
      expect(deserialized.entryPoint, original.entryPoint);
      expect(deserialized.dependencies, equals(original.dependencies));
      expect(deserialized.permissions, equals(original.permissions));
      expect(deserialized.configSchema, equals(original.configSchema));
      expect(deserialized.defaultConfig, equals(original.defaultConfig));
    });

    test('should handle malformed JSON with appropriate errors', () {
      // Given: Various malformed JSON scenarios
      final malformedJsonCases = [
        // Missing required fields
        <String, dynamic>{
          'name': 'incomplete',
          'display_name': 'Incomplete Connector',
          // Missing connector_id, description, category, version, author
        },

        // Invalid field types
        {
          'connector_id': 123, // Should be string
          'name': 'invalid-types',
          'display_name': 'Invalid Types',
          'description': 'Test invalid types',
          'category': 'test',
          'version': '1.0.0',
          'author': 'Test',
        },

        // Invalid nested structures
        {
          'connector_id': 'invalid-nested',
          'name': 'invalid-nested',
          'display_name': 'Invalid Nested',
          'description': 'Test invalid nested',
          'category': 'test',
          'version': '1.0.0',
          'author': 'Test',
          'config_schema': 'not-an-object', // Should be Map
        },
      ];

      for (final malformedJson in malformedJsonCases) {
        // Then: Should throw appropriate exceptions (catch any error type)
        expect(
          () => ConnectorDefinition.fromJson(malformedJson),
          throwsA(anything),
          reason:
              'Malformed JSON should throw some kind of error: $malformedJson',
        );
      }
    });
  });
}

// Helper functions for business logic validation
bool _isValidSemanticVersion(String version) {
  final semanticVersionRegex = RegExp(
      r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$');
  return semanticVersionRegex.hasMatch(version);
}

bool _isTerminalState(ConnectorState state) {
  return state == ConnectorState.error;
}

bool _requiresUserAction(ConnectorState state) {
  return [ConnectorState.error, ConnectorState.available].contains(state);
}

bool _isActiveState(ConnectorState state) {
  return state == ConnectorState.running;
}

bool _isStableState(ConnectorState state) {
  return [
    ConnectorState.running,
    ConnectorState.enabled,
    ConnectorState.configured
  ].contains(state);
}

bool _isTransitionalState(ConnectorState state) {
  return [
    ConnectorState.stopping,
    ConnectorState.updating,
    ConnectorState.uninstalling,
  ].contains(state);
}

bool _isConfigurationState(ConnectorState state) {
  return [
    ConnectorState.available,
    ConnectorState.installed,
    ConnectorState.configured,
    ConnectorState.enabled,
  ].contains(state);
}

bool _validateConnectorState(ConnectorInfo connector) {
  // Business rule: Running connectors must have a process ID
  if (connector.state == ConnectorState.running) {
    return connector.processId != null;
  }

  // Business rule: Non-running connectors should not have a process ID
  if ([ConnectorState.enabled, ConnectorState.configured, ConnectorState.error]
      .contains(connector.state)) {
    return connector.processId == null;
  }

  return true; // Other states are flexible
}
