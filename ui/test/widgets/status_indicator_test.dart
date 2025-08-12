import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:linch_mind/widgets/status_indicator.dart';

void main() {
  group('StatusIndicator', () {
    testWidgets('should display connected state correctly',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusIndicator(isConnected: true),
          ),
        ),
      );

      // Should show connected icon and text
      expect(find.byIcon(Icons.cloud_done), findsOneWidget);
      expect(find.text('Connected'), findsOneWidget);

      // Should use green color for connected state
      final container = tester.widget<Container>(find.byType(Container).first);
      final decoration = container.decoration as BoxDecoration;
      expect(decoration.color != null ? (decoration.color!.a * 255.0).round() & 0xff : 0,
          greaterThan(0)); // Should have some green color
    });

    testWidgets('should display disconnected state correctly',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusIndicator(isConnected: false),
          ),
        ),
      );

      // Should show disconnected icon and text
      expect(find.byIcon(Icons.cloud_off), findsOneWidget);
      expect(find.text('Disconnected'), findsOneWidget);
    });

    testWidgets('should display custom message when provided',
        (WidgetTester tester) async {
      const customMessage = 'Connecting...';

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

      expect(find.text(customMessage), findsOneWidget);
      expect(find.text('Disconnected'), findsNothing);
    });

    testWidgets('should handle tap callback', (WidgetTester tester) async {
      bool tapped = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: StatusIndicator(
              isConnected: true,
              onTap: () {
                tapped = true;
              },
            ),
          ),
        ),
      );

      await tester.tap(find.byType(StatusIndicator));
      expect(tapped, true);
    });

    testWidgets('should show tooltip on hover', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusIndicator(isConnected: true),
          ),
        ),
      );

      // Find the tooltip widget
      expect(find.byType(Tooltip), findsOneWidget);

      final tooltip = tester.widget<Tooltip>(find.byType(Tooltip));
      expect(tooltip.message, 'Connected');
    });

    testWidgets('should animate when connected', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusIndicator(isConnected: true),
          ),
        ),
      );

      // Should have AnimatedBuilder for pulse animation
      expect(find.byType(AnimatedBuilder), findsAtLeastNWidgets(1));

      // Advance animation and verify it's running
      await tester.pump(const Duration(seconds: 1));
      expect(find.byType(Transform), findsAtLeastNWidgets(1));
    });
  });

  group('StatusDot', () {
    testWidgets('should display active dot correctly',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusDot(isActive: true),
          ),
        ),
      );

      final container = tester.widget<Container>(find.byType(Container));
      final decoration = container.decoration as BoxDecoration;

      expect(decoration.shape, BoxShape.circle);
      expect(decoration.boxShadow, isNotNull);
      expect(decoration.boxShadow!.isNotEmpty, true);
    });

    testWidgets('should display inactive dot correctly',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusDot(isActive: false),
          ),
        ),
      );

      final container = tester.widget<Container>(find.byType(Container));
      final decoration = container.decoration as BoxDecoration;

      expect(decoration.shape, BoxShape.circle);
      expect(decoration.boxShadow, null);
    });

    testWidgets('should respect custom size', (WidgetTester tester) async {
      const customSize = 16.0;

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

      final container = tester.widget<Container>(find.byType(Container));
      expect(container.constraints?.maxWidth, customSize);
      expect(container.constraints?.maxHeight, customSize);
    });
  });

  group('StatusCard', () {
    testWidgets('should display healthy status card',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusCard(
              title: 'Test Service',
              isHealthy: true,
            ),
          ),
        ),
      );

      expect(find.text('Test Service'), findsOneWidget);
      expect(find.text('Healthy'), findsOneWidget);
      expect(find.byIcon(Icons.check_circle), findsOneWidget);
    });

    testWidgets('should display error status card with message',
        (WidgetTester tester) async {
      const errorMessage = 'Service is down';

      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusCard(
              title: 'Test Service',
              isHealthy: false,
              errorMessage: errorMessage,
            ),
          ),
        ),
      );

      expect(find.text('Test Service'), findsOneWidget);
      expect(find.text('Error'), findsOneWidget);
      expect(find.byIcon(Icons.error), findsOneWidget);
      expect(find.text(errorMessage), findsOneWidget);
      expect(find.byIcon(Icons.warning), findsOneWidget);
    });

    testWidgets('should display last update time', (WidgetTester tester) async {
      const lastUpdateTime = '2 minutes ago';

      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusCard(
              title: 'Test Service',
              isHealthy: true,
              lastUpdateTime: lastUpdateTime,
            ),
          ),
        ),
      );

      expect(
          find.textContaining('Last updated: $lastUpdateTime'), findsOneWidget);
      expect(find.byIcon(Icons.access_time), findsOneWidget);
    });

    testWidgets('should show retry button when callback provided',
        (WidgetTester tester) async {
      bool retryTapped = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: StatusCard(
              title: 'Test Service',
              isHealthy: false,
              onRetry: () {
                retryTapped = true;
              },
            ),
          ),
        ),
      );

      expect(find.text('Retry'), findsOneWidget);
      expect(find.byIcon(Icons.refresh), findsOneWidget);

      await tester.tap(find.text('Retry'));
      expect(retryTapped, true);
    });

    testWidgets('should show details button when callback provided',
        (WidgetTester tester) async {
      bool detailsTapped = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: StatusCard(
              title: 'Test Service',
              isHealthy: true,
              onViewDetails: () {
                detailsTapped = true;
              },
            ),
          ),
        ),
      );

      expect(find.text('Details'), findsOneWidget);
      expect(find.byIcon(Icons.info_outline), findsOneWidget);

      await tester.tap(find.text('Details'));
      expect(detailsTapped, true);
    });
  });
}
