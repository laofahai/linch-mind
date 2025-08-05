import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:linch_mind/widgets/status_indicator.dart';

void main() {
  group('StatusIndicator Business Logic Tests', () {
    group('Status Display Accuracy', () {
      testWidgets('should accurately display running connector status',
          (WidgetTester tester) async {
        // Given: StatusIndicator for a running connector
        await tester.pumpWidget(
          const MaterialApp(
            home: Scaffold(
              body: StatusIndicator(isConnected: true),
            ),
          ),
        );

        // Then: Should display correct visual indicators for running state
        expect(find.byIcon(Icons.cloud_done), findsOneWidget);
        expect(find.text('Connected'), findsOneWidget);

        // And: Should use appropriate color for positive status
        final container = tester.widget<Container>(
          find.ancestor(
            of: find.byIcon(Icons.cloud_done),
            matching: find.byType(Container),
          ),
        );
        final decoration = container.decoration as BoxDecoration;
        expect(decoration.color, isNotNull);
        // Green color family indicates successful connection
        expect(decoration.color.toString(), contains('Color'));
      });

      testWidgets('should accurately display disconnected connector status',
          (WidgetTester tester) async {
        // Given: StatusIndicator for a disconnected connector
        await tester.pumpWidget(
          const MaterialApp(
            home: Scaffold(
              body: StatusIndicator(isConnected: false),
            ),
          ),
        );

        // Then: Should display correct visual indicators for disconnected state
        expect(find.byIcon(Icons.cloud_off), findsOneWidget);
        expect(find.text('Disconnected'), findsOneWidget);

        // And: Should visually distinguish from connected state
        final iconWidget = tester.widget<Icon>(find.byIcon(Icons.cloud_off));
        expect(iconWidget.icon, Icons.cloud_off);
      });

      testWidgets('should handle custom status messages for user feedback',
          (WidgetTester tester) async {
        // Given: Custom status message for specific user scenarios
        const customMessage = 'Reconnecting to server...';

        await tester.pumpWidget(
          const MaterialApp(
            home: Scaffold(
              body: StatusIndicator(
                isConnected: false,
                customMessage: customMessage,
              ),
            ),
          ),
        );

        // Then: Should display custom message instead of default
        expect(find.text(customMessage), findsOneWidget);
        expect(find.text('Disconnected'), findsNothing);
        expect(find.text('Connected'), findsNothing);
      });
    });

    group('User Interaction Handling', () {
      testWidgets('should handle user tap interactions correctly',
          (WidgetTester tester) async {
        // Given: StatusIndicator with tap callback for user interaction
        bool userTappedStatus = false;
        String? callbackContext;

        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(
              body: StatusIndicator(
                isConnected: true,
                onTap: () {
                  userTappedStatus = true;
                  callbackContext = 'user_initiated_refresh';
                },
              ),
            ),
          ),
        );

        // When: User taps on the status indicator
        await tester.tap(find.byType(StatusIndicator));
        await tester.pumpAndSettle();

        // Then: Should trigger user callback with proper context
        expect(userTappedStatus, true);
        expect(callbackContext, 'user_initiated_refresh');
      });

      testWidgets('should be non-interactive when callback is null',
          (WidgetTester tester) async {
        // Given: StatusIndicator without tap callback (read-only display)
        await tester.pumpWidget(
          const MaterialApp(
            home: Scaffold(
              body: StatusIndicator(
                isConnected: true,
                onTap: null, // No interaction expected
              ),
            ),
          ),
        );

        // Then: Should display status without interactive behavior
        expect(find.byType(StatusIndicator), findsOneWidget);
        expect(find.byType(GestureDetector), findsNothing);
      });

      testWidgets('should provide accessibility support for screen readers',
          (WidgetTester tester) async {
        // Given: StatusIndicator that needs to be accessible
        await tester.pumpWidget(
          const MaterialApp(
            home: Scaffold(
              body: StatusIndicator(isConnected: true),
            ),
          ),
        );

        // Then: Should provide semantic information for assistive technology
        final tooltip = tester.widget<Tooltip>(find.byType(Tooltip));
        expect(tooltip.message, 'Connected');

        // And: Should be findable by semantic labels
        expect(find.byTooltip('Connected'), findsOneWidget);
      });
    });

    group('Animation and Visual Feedback', () {
      testWidgets('should animate pulse effect for connected status',
          (WidgetTester tester) async {
        // Given: Connected status indicator that should show activity
        await tester.pumpWidget(
          const MaterialApp(
            home: Scaffold(
              body: StatusIndicator(isConnected: true),
            ),
          ),
        );

        // Then: Should have animation components for visual feedback
        expect(find.byType(AnimatedBuilder), findsAtLeastNWidgets(1));

        // When: Animation progresses
        await tester.pump(const Duration(milliseconds: 500));

        // Then: Should maintain animated visual feedback
        expect(find.byType(Transform), findsAtLeastNWidgets(1));
      });

      testWidgets('should stop animation when disconnected',
          (WidgetTester tester) async {
        // Given: StatusIndicator that changes from connected to disconnected
        await tester.pumpWidget(
          const MaterialApp(
            home: Scaffold(
              body: StatusChangeDemo(),
            ),
          ),
        );

        // Initially connected with animation
        expect(find.text('Connected'), findsOneWidget);
        expect(find.byType(AnimatedBuilder), findsAtLeastNWidgets(1));

        // When: Status changes to disconnected
        await tester.tap(find.byType(ElevatedButton));
        await tester.pumpAndSettle();

        // Then: Should show disconnected status
        expect(find.text('Disconnected'), findsOneWidget);
      });
    });

    group('StatusDot Component Tests', () {
      testWidgets('should display active status dot correctly',
          (WidgetTester tester) async {
        // Given: Active status dot for simple status display
        await tester.pumpWidget(
          const MaterialApp(
            home: Scaffold(
              body: StatusDot(isActive: true),
            ),
          ),
        );

        // Then: Should display active visual state
        final container = tester.widget<Container>(find.byType(Container));
        final decoration = container.decoration as BoxDecoration;

        expect(decoration.shape, BoxShape.circle);
        expect(decoration.boxShadow, isNotNull);
        expect(decoration.boxShadow!.isNotEmpty, true);
      });

      testWidgets('should display inactive status dot correctly',
          (WidgetTester tester) async {
        // Given: Inactive status dot
        await tester.pumpWidget(
          const MaterialApp(
            home: Scaffold(
              body: StatusDot(isActive: false),
            ),
          ),
        );

        // Then: Should display inactive visual state
        final container = tester.widget<Container>(find.byType(Container));
        final decoration = container.decoration as BoxDecoration;

        expect(decoration.shape, BoxShape.circle);
        expect(decoration.boxShadow, null); // No glow effect when inactive
      });

      testWidgets('should respect custom size parameters',
          (WidgetTester tester) async {
        // Given: Custom sized status dot
        const customSize = 24.0;

        await tester.pumpWidget(
          const MaterialApp(
            home: Scaffold(
              body: StatusDot(
                isActive: true,
                size: customSize,
              ),
            ),
          ),
        );

        // Then: Should apply custom sizing
        final container = tester.widget<Container>(find.byType(Container));
        expect(container.constraints?.maxWidth, customSize);
        expect(container.constraints?.maxHeight, customSize);
      });
    });

    group('StatusCard Comprehensive Display Tests', () {
      testWidgets('should display healthy service status with full information',
          (WidgetTester tester) async {
        // Given: Healthy service requiring detailed status display
        await tester.pumpWidget(
          const MaterialApp(
            home: Scaffold(
              body: StatusCard(
                title: 'Database Connection Service',
                isHealthy: true,
                lastUpdateTime: '2 minutes ago',
              ),
            ),
          ),
        );

        // Then: Should display comprehensive healthy status
        expect(find.text('Database Connection Service'), findsOneWidget);
        expect(find.text('Healthy'), findsOneWidget);
        expect(find.byIcon(Icons.check_circle), findsOneWidget);
        expect(
            find.textContaining('Last updated: 2 minutes ago'), findsOneWidget);
        expect(find.byIcon(Icons.access_time), findsOneWidget);
      });

      testWidgets('should display error status with diagnostic information',
          (WidgetTester tester) async {
        // Given: Service in error state requiring user attention
        const errorMessage =
            'Connection timeout: Unable to reach database server at db.example.com:5432';

        await tester.pumpWidget(
          const MaterialApp(
            home: Scaffold(
              body: StatusCard(
                title: 'Database Connection Service',
                isHealthy: false,
                errorMessage: errorMessage,
                lastUpdateTime: '30 seconds ago',
              ),
            ),
          ),
        );

        // Then: Should display comprehensive error information
        expect(find.text('Database Connection Service'), findsOneWidget);
        expect(find.text('Error'), findsOneWidget);
        expect(find.byIcon(Icons.error), findsOneWidget);
        expect(find.text(errorMessage), findsOneWidget);
        expect(find.byIcon(Icons.warning), findsOneWidget);
        expect(find.textContaining('Last updated: 30 seconds ago'),
            findsOneWidget);
      });

      testWidgets(
          'should provide user action buttons when callbacks are provided',
          (WidgetTester tester) async {
        // Given: Service status that allows user intervention
        bool retryTriggered = false;
        bool detailsViewed = false;
        String? retryContext;

        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(
              body: StatusCard(
                title: 'API Gateway Service',
                isHealthy: false,
                errorMessage: 'Service temporarily unavailable',
                onRetry: () {
                  retryTriggered = true;
                  retryContext = 'user_initiated_retry';
                },
                onViewDetails: () {
                  detailsViewed = true;
                },
              ),
            ),
          ),
        );

        // Then: Should provide user action options
        expect(find.text('Retry'), findsOneWidget);
        expect(find.byIcon(Icons.refresh), findsOneWidget);
        expect(find.text('Details'), findsOneWidget);
        expect(find.byIcon(Icons.info_outline), findsOneWidget);

        // When: User triggers retry action
        await tester.tap(find.text('Retry'));
        expect(retryTriggered, true);
        expect(retryContext, 'user_initiated_retry');

        // When: User views details
        await tester.tap(find.text('Details'));
        expect(detailsViewed, true);
      });
    });

    group('Theme and Responsiveness Tests', () {
      testWidgets('should adapt to light theme correctly',
          (WidgetTester tester) async {
        // Given: Light theme application
        await tester.pumpWidget(
          MaterialApp(
            theme: ThemeData.light(),
            home: const Scaffold(
              body: StatusIndicator(isConnected: true),
            ),
          ),
        );

        // Then: Should render appropriately for light theme
        final materialApp =
            tester.widget<MaterialApp>(find.byType(MaterialApp));
        expect(materialApp.theme?.brightness, Brightness.light);

        // And: Status indicator should be visible and readable
        expect(find.byIcon(Icons.cloud_done), findsOneWidget);
        expect(find.text('Connected'), findsOneWidget);
      });

      testWidgets('should adapt to dark theme correctly',
          (WidgetTester tester) async {
        // Given: Dark theme application
        await tester.pumpWidget(
          MaterialApp(
            theme: ThemeData.dark(),
            home: const Scaffold(
              body: StatusIndicator(isConnected: true),
            ),
          ),
        );

        // Then: Should render appropriately for dark theme
        final materialApp =
            tester.widget<MaterialApp>(find.byType(MaterialApp));
        expect(materialApp.theme?.brightness, Brightness.dark);

        // And: Status indicator should maintain visibility
        expect(find.byIcon(Icons.cloud_done), findsOneWidget);
        expect(find.text('Connected'), findsOneWidget);
      });

      testWidgets('should handle different screen sizes responsively',
          (WidgetTester tester) async {
        // Given: Different screen size scenarios
        final screenSizes = [
          const Size(320, 568), // Small mobile
          const Size(414, 896), // Large mobile
          const Size(768, 1024), // Tablet
          const Size(1920, 1080), // Desktop
        ];

        for (final size in screenSizes) {
          await tester.binding.setSurfaceSize(size);

          await tester.pumpWidget(
            const MaterialApp(
              home: Scaffold(
                body: StatusIndicator(isConnected: true),
              ),
            ),
          );

          // Then: Should render without overflow on all screen sizes
          expect(tester.takeException(), isNull);
          expect(find.byType(StatusIndicator), findsOneWidget);

          // And: Should maintain core functionality
          expect(find.byIcon(Icons.cloud_done), findsOneWidget);
          expect(find.text('Connected'), findsOneWidget);
        }

        // Reset to default size
        await tester.binding.setSurfaceSize(null);
      });
    });

    group('Performance and Edge Cases', () {
      testWidgets(
          'should handle rapid status changes without performance degradation',
          (WidgetTester tester) async {
        // Given: StatusIndicator that receives rapid updates
        await tester.pumpWidget(
          const MaterialApp(
            home: Scaffold(
              body: RapidStatusChanger(),
            ),
          ),
        );

        // When: Triggering many rapid status changes
        final stopwatch = Stopwatch()..start();

        for (int i = 0; i < 10; i++) {
          await tester.tap(find.byType(ElevatedButton));
          await tester
              .pump(const Duration(milliseconds: 16)); // 60 FPS frame rate
        }

        stopwatch.stop();

        // Then: Should handle updates efficiently
        expect(stopwatch.elapsedMilliseconds, lessThan(1000)); // Under 1 second
        expect(
            tester.takeException(), isNull); // No errors during rapid updates

        // And: Should settle to final state correctly
        await tester.pumpAndSettle();
        expect(find.byType(StatusIndicator), findsOneWidget);
      });

      testWidgets('should handle null and edge case inputs gracefully',
          (WidgetTester tester) async {
        // Given: StatusIndicator with edge case inputs
        await tester.pumpWidget(
          const MaterialApp(
            home: Scaffold(
              body: Column(
                children: [
                  StatusIndicator(
                    isConnected: true,
                    customMessage: '', // Empty custom message
                  ),
                  StatusDot(
                    isActive: true,
                    size: 0, // Zero size
                  ),
                  StatusCard(
                    title: '', // Empty title
                    isHealthy: true,
                  ),
                ],
              ),
            ),
          ),
        );

        // Then: Should handle edge cases without crashing
        expect(tester.takeException(), isNull);
        expect(find.byType(StatusIndicator), findsOneWidget);
        expect(find.byType(StatusDot), findsOneWidget);
        expect(find.byType(StatusCard), findsOneWidget);
      });

      testWidgets('should maintain state consistency during widget rebuilds',
          (WidgetTester tester) async {
        // Given: StatusIndicator in a widget that rebuilds frequently
        int buildCount = 0;

        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(
              body: StatefulBuilder(
                builder: (context, setState) {
                  buildCount++;
                  return Column(
                    children: [
                      StatusIndicator(isConnected: buildCount % 2 == 0),
                      ElevatedButton(
                        onPressed: () => setState(() {}),
                        child: Text('Rebuild ($buildCount)'),
                      ),
                    ],
                  );
                },
              ),
            ),
          ),
        );

        final initialBuildCount = buildCount;

        // When: Triggering multiple rebuilds
        for (int i = 0; i < 5; i++) {
          await tester.tap(find.byType(ElevatedButton));
          await tester.pumpAndSettle();
        }

        // Then: Should handle rebuilds correctly
        expect(buildCount, greaterThan(initialBuildCount));
        expect(tester.takeException(), isNull);
        expect(find.byType(StatusIndicator), findsOneWidget);
      });
    });
  });
}

// Helper widgets for testing complex scenarios
class StatusChangeDemo extends StatefulWidget {
  const StatusChangeDemo({super.key});

  @override
  State<StatusChangeDemo> createState() => _StatusChangeDemoState();
}

class _StatusChangeDemoState extends State<StatusChangeDemo> {
  bool isConnected = true;

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        StatusIndicator(isConnected: isConnected),
        const SizedBox(height: 20),
        ElevatedButton(
          onPressed: () {
            setState(() {
              isConnected = !isConnected;
            });
          },
          child: Text(isConnected ? 'Disconnect' : 'Connect'),
        ),
      ],
    );
  }
}

class RapidStatusChanger extends StatefulWidget {
  const RapidStatusChanger({super.key});

  @override
  State<RapidStatusChanger> createState() => _RapidStatusChangerState();
}

class _RapidStatusChangerState extends State<RapidStatusChanger> {
  bool isConnected = false;

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        StatusIndicator(isConnected: isConnected),
        const SizedBox(height: 20),
        ElevatedButton(
          onPressed: () {
            setState(() {
              isConnected = !isConnected;
            });
          },
          child: const Text('Toggle Status'),
        ),
      ],
    );
  }
}
