import 'package:flutter_test/flutter_test.dart';

import 'package:app/main.dart';

void main() {
  testWidgets("AutoAI app loads", (WidgetTester tester) async {
    await tester.pumpWidget(const AutoAIApp());

    expect(find.text("Dickson's autoAI"), findsOneWidget);
    expect(find.text("Automation control center"), findsOneWidget);
  });
}
