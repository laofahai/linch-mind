import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:linch_mind/main.dart';

void main() {
  testWidgets('Counter increments smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const LinchMindApp());

    // Verify that our app starts correctly
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
